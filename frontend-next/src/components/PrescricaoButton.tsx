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
        onClick={() => setShowModal(true)}
        className="rounded-md bg-blue-900/30 px-3 py-2 text-xs font-semibold text-blue-200 transition hover:bg-blue-900/50"
      >
        Ver Decisão
      </button>

      <PrescricaoModal
        machineId={machineId}
        isOpen={showModal}
        onClose={() => setShowModal(false)}
      />
    </>
  );
}