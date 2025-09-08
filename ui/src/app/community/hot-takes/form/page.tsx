"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Flame } from "lucide-react";
import Navigation from "@/components/navigation";

export default function SubmitHotTakePage() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    content: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<
    "idle" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState("");

  const handleInputChange = (
    e: React.ChangeEvent<HTMLTextAreaElement | HTMLInputElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitStatus("idle");
    setErrorMessage("");

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/takes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: formData.content,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Submission failed");
      }

      const data = await res.json();

      // ✅ redirect to the new take detail page (example route)
      router.push(`/hot-takes/${data.take_id}`);
    } catch (err: unknown) {
      console.error(err);

      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("An unknown error occurred");
      }

      setSubmitStatus("error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const isFormValid = !!formData.content;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Navigation />
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">
              Submit a Hot Take
            </h1>
            <p className="mt-2 text-gray-600 max-w-2xl mx-auto">
              Share your hottest basketball takes. Our AI will analyze them for
              truthfulness and provide insights, while the community can weigh
              in too.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {submitStatus === "error" && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3" />
            <div>
              <h3 className="text-red-800 font-semibold">Submission Failed</h3>
              <p className="text-red-700 text-sm">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Form */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Flame className="w-5 h-5 text-orange-600 mr-2" />
                Your Hot Take
              </h2>

              <div>
                <label
                  htmlFor="content"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Hot Take *
                </label>
                <textarea
                  id="content"
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-black transition-colors"
                  placeholder="LeBron would average 50 points per game in the 80s..."
                  rows={5}
                  required
                />
              </div>
            </div>

            <div className="pt-4">
              <button
                type="submit"
                disabled={!isFormValid || isSubmitting}
                className="w-full bg-orange-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-orange-700 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Submitting...
                  </>
                ) : (
                  "Submit Hot Take"
                )}
              </button>

              {!isFormValid && (
                <p className="mt-2 text-sm text-gray-500 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  Please enter your hot take
                </p>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
