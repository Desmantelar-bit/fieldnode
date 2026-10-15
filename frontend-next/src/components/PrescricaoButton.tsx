'use client';

import { useState } from 'react';
import { PrescricaoModal } from '@/components/PrescricaoModal';

interface PrescricaoButtonProps {
  machineId: string;
}

export function PrescricaoButton({ machineId }: PrescricaoButtonProps) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <button
        type="button"
        onClick={() => setShowModal(true)}
        className="rounded-xl bg-[var(--panel-glass-mid)] px-3 py-2 text-xs font-semibold text-[var(--text-2)] transition hover:bg-[var(--panel-glass-strong)] hover:text-[var(--text-1)] active:scale-95"
      >
        Decisão IA
      </button>

      <PrescricaoModal
        machineId={machineId}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
      />
    </>
  );
}
