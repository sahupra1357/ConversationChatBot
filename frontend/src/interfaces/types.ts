export type Conversation = {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
};

export type Message = {
  id: string;
  conversationId: string;
  content: string;
  isBot: boolean;
  createdAt: string;
};

export type User = {
  id: string;
  username: string;
  email: string;
  createdAt: string;
};
