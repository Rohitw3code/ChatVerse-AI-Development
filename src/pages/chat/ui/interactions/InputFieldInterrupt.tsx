import React from 'react';
import { ApiMessage } from "../types";

interface InputFieldInterruptProps {
    messageData: ApiMessage['data'];
}

export function InputFieldInterrupt({ messageData }: InputFieldInterruptProps) {
    const { title } = messageData?.data || {};

    if (!title) return null;

    return (
        <div>
            <div className="font-semibold text-violet-300">{title}</div>
        </div>
    );
}