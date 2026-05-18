import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

import {
  Upload,
  Send,
  FileText,
  Bot,
  User,
  Sparkles
} from "lucide-react";

function App() {

  const [file, setFile] = useState(null);

  const [query, setQuery] = useState("");

  const [messages, setMessages] = useState([]);

  const [loading, setLoading] = useState(false);

  const [atsReport, setAtsReport] = useState("");

  const uploadResume = async () => {

    if (!file) {

      alert("Please select a resume");

      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    setLoading(true);

    try {

      await axios.post(
        "http://127.0.0.1:8000/upload",
        formData
      );

      alert("Resume uploaded successfully");

    } catch (error) {

      console.error(error);

      alert("Upload failed");
    }

    setLoading(false);
  };

  const askQuestion = async () => {

    if (!query) return;

    const userMessage = {
      role: "user",
      content: query
    };

    setMessages((prev) => [
      ...prev,
      userMessage
    ]);

    setLoading(true);

    try {

      const res = await axios.post(
        "http://127.0.0.1:8000/chat",
        {
          query
        }
      );

      const aiMessage = {
        role: "ai",
        content: String(
          res.data.response
        )
      };

      setMessages((prev) => [
        ...prev,
        aiMessage
      ]);

    } catch (error) {

      console.error(error);

      const errorMessage = {
        role: "ai",
        content:
          "Something went wrong"
      };

      setMessages((prev) => [
        ...prev,
        errorMessage
      ]);
    }

    setQuery("");

    setLoading(false);
  };

  const getATSScore = async () => {

    setLoading(true);

    try {

      const res = await axios.get(
        "http://127.0.0.1:8000/ats"
      );

      setAtsReport(
        String(res.data.response)
      );

    } catch (error) {

      console.error(error);

      alert("ATS analysis failed");
    }

    setLoading(false);
  };

  return (

    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-black to-gray-900 text-white">

      <div className="max-w-6xl mx-auto p-8">

        {/* HEADER */}

        <div className="text-center mb-10">

          <div className="flex items-center justify-center gap-3 mb-4">

            <Sparkles
              className="text-cyan-400"
              size={40}
            />

            <h1 className="text-6xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">

              Resume RAG AI

            </h1>

          </div>

          <p className="text-gray-400 text-lg">

            AI-powered Resume Intelligence Platform

          </p>

        </div>

        {/* UPLOAD SECTION */}

        <div className="bg-gray-900 border border-gray-800 rounded-3xl p-8 shadow-2xl mb-8">

          <div className="flex items-center gap-3 mb-6">

            <Upload className="text-cyan-400" />

            <h2 className="text-3xl font-bold">

              Upload Resume

            </h2>

          </div>

          <div className="flex flex-col md:flex-row gap-4 items-center">

            <input
              type="file"
              accept=".pdf"
              onChange={(e) =>
                setFile(e.target.files[0])
              }
              className="bg-gray-800 border border-gray-700 rounded-xl p-3 w-full"
            />

            <button
              onClick={uploadResume}
              className="bg-cyan-500 hover:bg-cyan-600 transition-all px-8 py-3 rounded-xl font-semibold flex items-center gap-2"
            >

              <Upload size={18} />

              Upload

            </button>

            <button
              onClick={getATSScore}
              className="bg-green-600 hover:bg-green-700 transition-all px-8 py-3 rounded-xl font-semibold flex items-center gap-2"
            >

              <FileText size={18} />

              ATS Analysis

            </button>

          </div>

        </div>

        {/* CHAT SECTION */}

        <div className="bg-gray-900 border border-gray-800 rounded-3xl shadow-2xl p-8">

          <div className="flex items-center gap-3 mb-6">

            <Bot className="text-blue-400" />

            <h2 className="text-3xl font-bold">

              Chat with Resume

            </h2>

          </div>

          {/* CHAT BOX */}

          <div className="h-[500px] overflow-y-auto bg-gray-950 border border-gray-800 rounded-2xl p-6 mb-6">

            {messages.length === 0 && (

              <div className="flex flex-col items-center justify-center h-full text-gray-500">

                <Bot
                  size={60}
                  className="mb-4 opacity-50"
                />

                <p className="text-xl">

                  Ask AI anything about the resume...

                </p>

              </div>
            )}

            {messages.map((msg, index) => (

              <div
                key={index}
                className={`mb-6 flex ${
                  msg.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >

                <div
                  className={`max-w-[80%] px-6 py-4 rounded-2xl shadow-lg ${
                    msg.role === "user"
                      ? "bg-cyan-500 text-white"
                      : "bg-gray-800 border border-gray-700 text-gray-100"
                  }`}
                >

                  <div className="flex items-center gap-2 mb-2">

                    {
                      msg.role === "user"
                        ? <User size={18} />
                        : <Bot size={18} />
                    }

                    <span className="font-semibold">

                      {
                        msg.role === "user"
                          ? "You"
                          : "AI Assistant"
                      }

                    </span>

                  </div>

                  <div className="prose prose-invert max-w-none">

                    <ReactMarkdown>

                      {String(msg.content)}

                    </ReactMarkdown>

                  </div>

                </div>

              </div>
            ))}

            {loading && (

              <div className="text-gray-400 animate-pulse">

                AI is analyzing...

              </div>
            )}

          </div>

          {/* INPUT */}

          <div className="flex gap-4">

            <input
              type="text"
              placeholder="Ask a question about the resume..."
              value={query}
              onChange={(e) =>
                setQuery(e.target.value)
              }
              onKeyDown={(e) => {

                if (e.key === "Enter") {
                  askQuestion();
                }
              }}
              className="flex-1 bg-gray-950 border border-gray-700 rounded-2xl p-4 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />

            <button
              onClick={askQuestion}
              className="bg-blue-600 hover:bg-blue-700 transition-all px-8 rounded-2xl flex items-center gap-2 font-semibold"
            >

              <Send size={18} />

              Send

            </button>

          </div>

        </div>

        {/* ATS REPORT */}

        {
          atsReport && (

            <div className="bg-gray-900 border border-gray-800 rounded-3xl shadow-2xl p-8 mt-8">

              <div className="flex items-center gap-3 mb-6">

                <FileText className="text-green-400" />

                <h2 className="text-3xl font-bold">

                  ATS Analysis Report

                </h2>

              </div>

              <div className="bg-gray-950 border border-gray-800 rounded-2xl p-6 prose prose-invert max-w-none">

                <ReactMarkdown>

                  {String(atsReport)}

                </ReactMarkdown>

              </div>

            </div>
          )
        }

      </div>

    </div>
  );
}

export default App;