const base_url = import.meta.env.VITE_AI_API_BASE_URL

export const ChatAgentApiService = {
  sendMessageStream: (params: { message: string; provider_id: string,chat_id:string, human_response:boolean}) => {
    const eventSource = new EventSource(
      `${base_url}/chatagent/chat/send-message-stream?message=${encodeURIComponent(params.message
      )}&provider_id=${params.provider_id}&chat_id=${params.chat_id}&human_response=${params.human_response}`
    );
    return eventSource;
  },

  getThreads: async (provider_id: string) => {
    const response = await fetch(`${base_url}/chatagent/chat/threads?provider_id=${provider_id}`);
    if (!response.ok) {
      console.error("Failed to fetch threads");
      return [];
    }
    return response.json();
  },

  getChatHistory: async (provider_id: string, thread_id: string, page: number = 1, limit: number = 30) => {
    const response = await fetch(`${base_url}/chatagent/chat/history?provider_id=${provider_id}&thread_id=${thread_id}&page=${page}&limit=${limit}`);
    if (!response.ok) {
      console.error("Failed to fetch chat history");
      return [];
    }
    return response.json();
  },

  deleteThread: async (thread_id: string) => {
    const response = await fetch(`${base_url}/chatagent/chat/threads/${thread_id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      console.error("Failed to delete thread");
      return { success: false, message: "Failed to delete thread" };
    }
    return response.json();
  },

  updateMessageData: async (params: {
    id: number;
    thread_id: string;
    query_id: string;
    data: any;
    merge?: boolean;
  }) => {
    const response = await fetch(`${base_url}/chatagent/chat/update-data`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });
    if (!response.ok) {
      console.error("Failed to update message data");
      throw new Error("Failed to update message data");
    }
    return response.json();
  },
};