import os, socket, docker, requests, secrets, time
from datetime import datetime, timedelta
from werkzeug.exceptions import InternalServerError

try:
    docker_client = docker.DockerClient(base_url="tcp://ssh-tunnel:2375")
except Exception:
    docker_client = None

CLOUDFLARE_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
TUNNEL_ID = os.getenv("CLOUDFLARE_TUNNEL_ID")
DOMAIN = os.getenv("CLOUDFLARE_DOMAIN")

def _get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def _manage_cloudfare_tunnels(subdomain, local_port=None, action="ADD"):
    if not all([CLOUDFLARE_TOKEN, ACCOUNT_ID, TUNNEL_ID, DOMAIN]):
        raise InternalServerError("CLOUDFLARE_CONFIG_ERROR|Configuration Cloudflare manquante.")
    tunnel_url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/cfd_tunnel/{TUNNEL_ID}/configurations"
    zone_url = f"https://api.cloudflare.com/client/v4/zones?name={DOMAIN}"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        target_hostname = f"{subdomain}.{DOMAIN}"
        response = requests.get(tunnel_url, headers=headers)
        if response.status_code != 200:
            raise InternalServerError(f"INSTANCES_API_ERROR|Erreur lors de la récupération du tunnel: {response.text}")
        config_data = response.json().get("result", {}).get("config", {})
        ingress_rules = config_data.get("ingress", [])
        ingress_rules = [rule for rule in ingress_rules if rule.get("hostname") != target_hostname]
        catch_all_rule = next((rule for rule in ingress_rules if "hostname" not in rule), {"service": "http_status:404"})
        ingress_rules = [rule for rule in ingress_rules if "hostname" in rule]
        if action == "ADD":
            if not local_port:
                raise InternalServerError("INSTANCES_API_ERROR|Port local manquant pour l'ajout du tunnel.")
            new_rule = {
                "hostname": target_hostname,
                "service": f"http://172.17.0.1:{local_port}"
            }
            ingress_rules.insert(0, new_rule)
        ingress_rules.append(catch_all_rule)
        payload = {"config": {"ingress": ingress_rules}}
        update_res = requests.put(tunnel_url, headers=headers, json=payload)
        if update_res.status_code != 200:
            raise InternalServerError("INSTANCES_API_ERROR|Erreur lors de la mise à jour des règles du tunnel.")
        zone_res = requests.get(zone_url, headers=headers)
        zones = zone_res.json().get("result", [])
        if not zones:
            raise InternalServerError(f"DNS_ERROR|Impossible de trouver la zone DNS pour {DOMAIN}")
        zone_id = zones[0]["id"]
        dns_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        if action == "ADD":
            dns_payload = {
                "type": "CNAME",
                "name": target_hostname,
                "content": f"{TUNNEL_ID}.cfargotunnel.com",
                "ttl": 1,
                "proxied": True
            }
            dns_res = requests.post(dns_url, headers=headers, json=dns_payload)
            if dns_res.status_code not in [200, 201]:
                raise InternalServerError("DNS_ERROR|Erreur lors de la création de l'enregistrement DNS.")
        elif action == "REMOVE":
            dns_search = requests.get(f"{dns_url}?name={target_hostname}", headers=headers)
            records = dns_search.json().get("result", [])
            for r in records:
                requests.delete(f"{dns_url}/{r['id']}", headers=headers)
                
        return f"https://{target_hostname}"
    except InternalServerError:
        raise
    except Exception as e:
        raise InternalServerError(f"INSTANCES_API_ERROR|Erreur lors de la gestion des instances: {str(e)}")


def create_user_instance(user_id, challenge_id, challenge_flag, image_name, internal_port):
    if not docker_client:
        raise InternalServerError("DOCKER_CLIENT_ERROR|Impossible de se connecter au client Docker.")
    suffix = secrets.token_urlsafe(16).lower().replace('_', '-').replace('.', '-')
    subdomain = f"user{user_id}-ch{challenge_id}-{suffix}"
    container_name = f"gh-instance-{subdomain}"
    local_port = _get_free_port()
    try:
        container = docker_client.containers.run(
            image=image_name,
            name=container_name,
            detach=True,
            ports={f'{internal_port}/tcp': local_port},
            environment={
                "FLAG": challenge_flag,
                "USER_ID": str(user_id)
            },
            mem_limit='512m',
            nano_cpus=500000000,
            restart_policy={"Name": "no"}
        )
    except Exception as e:
        raise InternalServerError(f"DOCKER_RUN_ERROR|Erreur lors du lancement du conteneur: {str(e)}")
    try:
        cf_url = _manage_cloudfare_tunnels(subdomain, local_port, action="ADD")
    except Exception as e:
        container.remove(force=True)
        raise e
    time.sleep(6)
    expires_at_dt = datetime.now() + timedelta(hours=1)
    return {
        "container_id": container.id,
        "container_name": container_name,
        "subdomain": subdomain,
        "url": cf_url,
        "local_port": local_port,
        "challenge_flag": challenge_flag,
        "expires_at": expires_at_dt
    }


def stop_user_instance(container_name, subdomain):
    _manage_cloudfare_tunnels(subdomain, action="REMOVE")
    if docker_client:
        try:
            container = docker_client.containers.get(container_name)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass
        except Exception as e:
            raise InternalServerError(f"DOCKER_STOP_ERROR|Erreur lors de la suppression du conteneur: {str(e)}")

