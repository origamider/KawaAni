"use client";

import { useEffect, useRef } from "react";

// Reactと仮想DOMの関係:https://qiita.com/seira/items/6767e222890c9890ecb9
// useRefってなんで使うのか: https://qiita.com/lvn-awano/items/cfe1baa7b4717cbb5f44
// ref:モダンなモーダル実装例: https://tech.excite.co.jp/entry/2024/12/17/172023
// ref:HTMLDialogElement:showModal()のデメリット https://techracho.bpsinc.jp/baba/2024_09_05/144320
type ModalProps = {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
};

// ref: https://web.dev/learn/html/dialog (showModal()で背景inert化・フォーカストラップ・Escキー対応が自動で付く)
export default function Modal({ isOpen, onClose, children }: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {// useEffectはコンポーネント外の処理を扱うフック。
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (isOpen && !dialog.open) {
      dialog.showModal();
    } else if (!isOpen && dialog.open) {
      dialog.close();
    }
  }, [isOpen]);

  return (
    <dialog
      ref={dialogRef}
      onClose={onClose}
      className="relative m-auto w-full max-w-md rounded-2xl border border-line bg-surface p-6 text-text backdrop:bg-black/70"
    >
      <button
        onClick={onClose}
        aria-label="閉じる"
        className="absolute top-4 right-4 flex h-8 w-8 items-center justify-center rounded-full text-text-soft transition-colors duration-150 hover:bg-white/[0.06] hover:text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
          <path
            d="M1 1L13 13M13 1L1 13"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
      </button>
      {children}
    </dialog>
  );
}
