import { Message } from "../../interfaces";
import { useToast } from "@/hooks/use-toast";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const { toast } = useToast();

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copied to clipboard",
        description: "Message content has been copied to your clipboard.",
      });
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Could not copy message to clipboard.",
        variant: "destructive",
      });
    }
  };
  if (message.isBot) {
    return (
      <div className="flex items-start space-x-3 animate-fade-in">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-emerald-500 rounded-full flex items-center justify-center flex-shrink-0">
          <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <div className="flex-1 max-w-3xl">
          <div className="bg-white rounded-2xl rounded-tl-md shadow-sm border border-gray-200 p-4">
            <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">{message.content}</div>
          </div>
          <div className="flex items-center justify-between mt-2 px-1">
            <span className="text-xs text-gray-400">AI Assistant • {new Date(message.createdAt).toLocaleTimeString()}</span>
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => copyToClipboard(message.content)}
                className="p-1 hover:bg-gray-100 rounded transition-colors"
                title="Copy message"
              >
                <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
              <button 
                className="p-1 hover:bg-gray-100 rounded transition-colors"
                title="Like message"
              >
                <svg className="w-3 h-3 text-gray-400 hover:text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                </svg>
              </button>
              <button 
                className="p-1 hover:bg-gray-100 rounded transition-colors"
                title="Dislike message"
              >
                <svg className="w-3 h-3 text-gray-400 hover:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06L20 4m-10 10v5a2 2 0 002 2h.095a.905.905 0 00.905-.905 0-.714.211-1.412.608-2.006L20 13V4m-10 10H8m12 0h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start space-x-3 justify-end animate-fade-in">
      <div className="flex-1 max-w-3xl">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl rounded-tr-md shadow-sm p-4 ml-auto">
          <div className="text-white leading-relaxed whitespace-pre-wrap">{message.content}</div>
        </div>
        <div className="flex items-center justify-end mt-2 px-1">
          <span className="text-xs text-gray-400">You • {new Date(message.createdAt).toLocaleTimeString()}</span>
        </div>
      </div>
      <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
        <span className="text-white text-sm font-medium">JD</span>
      </div>
    </div>
  );
}
