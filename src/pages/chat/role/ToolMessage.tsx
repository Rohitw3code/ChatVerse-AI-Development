import { ApiMessage } from "../types";
import { ToolExecution } from "../type/ToolExecution";

interface ToolMessageProps {
  message: ApiMessage;
}

export function ToolMessage({ message }: ToolMessageProps) {
  return (
    <div className="flex w-full justify-start mb-5">
      <ToolExecution message={message} />
    </div>
  );
}