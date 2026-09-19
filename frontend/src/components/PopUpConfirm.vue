<script setup>
    defineProps({
    isOpen: { type: Boolean, required: true },
    title: { type: String, default: 'Confirmation' },
    message: { type: String, required: true },
    confirmText: { type: String, default: 'Confirmer' },
    cancelText: { type: String, default: 'Annuler' },
    loading: { type: Boolean, default: false }
    })

defineEmits(['confirm', 'cancel'])
</script>

<template>
    <dialog :class="['modal', { 'modal-open': isOpen }]">
        <div class="modal-box bg-base-100 border border-base-300 rounded-none shadow-2xl p-6 max-w-md">
        <div class="flex items-center justify-between border-b border-base-300 pb-3 mb-4">
            <h3 class="font-titre font-bold text-base text-primary uppercase tracking-wider">{{ title }}</h3>
            <button @click="$emit('cancel')" class="btn btn-sm btn-ghost font-code">✕</button>
        </div>
        <p class="font-text text-xs text-base-content/80 leading-relaxed mb-6">
            {{ message }}
        </p>
        <div class="modal-action mt-2 pt-3 border-t border-base-300 flex justify-end gap-2">
            <button @click="$emit('cancel')" class="btn btn-sm btn-ghost font-code text-xs">{{ cancelText }}</button>
            <button @click="$emit('confirm')" :disabled="loading" class="btn btn-error btn-sm font-text font-bold tracking-wider relative flex items-center justify-center">
                <span v-if="loading" class="loading loading-spinner loading-xs absolute"></span>
                <span :class="{ 'opacity-0': loading }">Confirmer</span>
            </button>
        </div>
        </div>
        <form method="dialog" class="modal-backdrop">
        <button @click="$emit('cancel')">fermer</button>
        </form>
    </dialog>
</template>