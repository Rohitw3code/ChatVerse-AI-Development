import { ApiMessage } from "../../types";

export function makeInsufficientCreditsMessage(
  providerId: string,
  chatId: string,
  errorData: { message: string; current_credits: number }
): ApiMessage {
  return {
    provider_id: providerId!,
    thread_id: chatId!,
    role: "system_error",
    node: "error",
    status: "error",
    reason: "Insufficient credits",
    current_messages: [
      {
        role: "system",
        content: `${errorData.message} You currently have ${errorData.current_credits} credits. [Upgrade Plan](/pricing) to continue using AI features.`,
      },
    ],
    type_: "system",
  };
}
