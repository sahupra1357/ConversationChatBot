import { useState, useRef, useEffect } from "react";

interface MessageInputProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const suggestedPrompts = [
  "💡 Explain React hooks",
  "🎨 UI design principles", 
  "🚀 Performance optimization",
  "📱 Mobile responsiveness"
];

export default function MessageInput({ onSendMessage, disabled, placeholder }: MessageInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 128) + 'px';
  };

  const useSuggestion = (prompt: string) => {
    const cleanPrompt = prompt.replace(/^[💡🎨🚀📱]\s*/, '');
    setMessage(cleanPrompt);
    textareaRef.current?.focus();
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [message]);

  const defaultPlaceholder = "Type your message here... (Press Shift+Enter for new line)";

  return (
    <div className="bg-white border-t border-gray-200 p-4 lg:p-6">
      <div className="max-w-4xl mx-auto">
        <div className="relative">
          <div className="flex items-end space-x-4">
            <div className="flex-1">
              <div className="relative">
                <textarea
                  ref={textareaRef}
                  value={message}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  placeholder={placeholder || defaultPlaceholder}
                  className={`w-full resize-none rounded-2xl border ${disabled ? 'border-gray-200 bg-gray-100' : 'border-gray-300 bg-gray-50'} px-4 py-3 pr-12 focus:border-blue-600 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-600/20 transition-all duration-200 max-h-32 min-h-[2.75rem] ${disabled ? 'text-gray-400' : 'text-gray-800'}`}
                  rows={1}
                  disabled={disabled}
                />
                <button 
                  className="absolute right-2 bottom-2 p-2 text-gray-400 hover:text-gray-600 transition-colors disabled:text-gray-300"
                  title="Attach file"
                  disabled={disabled}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                </button>
              </div>
              <div className="flex items-center justify-between mt-2 px-1">
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span>Press <kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs">Enter</kbd> to send</span>
                  <span>•</span>
                  <span><kbd className="px-1 py-0.5 bg-gray-200 rounded text-xs">Shift+Enter</kbd> for new line</span>
                </div>
                <div className="flex items-center space-x-2">
                  <button 
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:hover:bg-transparent"
                    title="Voice message"
                    disabled={disabled}
                  >
                    <svg className={`w-4 h-4 ${disabled ? 'text-gray-300' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                  </button>
                  <button 
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:hover:bg-transparent"
                    title="Attach file"
                    disabled={disabled}
                  >
                    <svg className={`w-4 h-4 ${disabled ? 'text-gray-300' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            <button
              onClick={handleSubmit}
              disabled={disabled || !message.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-2xl transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ transform: 'rotate(90deg)' }}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>

        {/* Suggested Prompts - Hide when input is disabled */}
        {!disabled && (
          <div className="mt-4">
            <div className="flex flex-wrap gap-2">
              {suggestedPrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => useSuggestion(prompt)}
                  className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-full border border-gray-200 transition-colors"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
