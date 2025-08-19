'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, User, Ruler, Weight, Target, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react';

export default function SubmitPlayerPage() {
    const [formData, setFormData] = useState({
        name: '',
        height: '',
        weight: '',
        position: '',
        espnLink: '',
        sports247Link: '',
        rivalsLink: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
        ...prev,
        [name]: value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        
        // Simulate API call
        setTimeout(() => {
        setIsSubmitting(false);
        setSubmitStatus('success');
        // Reset form after success
        setTimeout(() => {
            setFormData({
            name: '',
            height: '',
            weight: '',
            position: '',
            espnLink: '',
            sports247Link: '',
            rivalsLink: ''
            });
            setSubmitStatus('idle');
        }, 3000);
        }, 2000);
    };

    const isFormValid = formData.name && formData.height && formData.weight && formData.position;

    return (
        <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <Link
                href="/"
                className="inline-flex items-center text-gray-600 hover:text-orange-600 transition-colors mb-4"
            >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
            </Link>
            
            <div className="text-center">
                <h1 className="text-3xl font-bold text-gray-900">Submit Missing Player</h1>
                <p className="mt-2 text-gray-600 max-w-2xl mx-auto">
                Help us expand our database by submitting information about high school players 
                who aren't currently in our system. Our AI will generate a comprehensive scouting report.
                </p>
            </div>
            </div>
        </div>

        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Success Message */}
            {submitStatus === 'success' && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 mr-3" />
                <div>
                <h3 className="text-green-800 font-semibold">Player Submitted Successfully!</h3>
                <p className="text-green-700 text-sm">
                    We'll review the information and generate an AI scouting report within 24-48 hours.
                </p>
                </div>
            </div>
            )}

            {/* Form */}
            <div className="bg-white rounded-lg shadow-sm p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Information */}
                <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <User className="w-5 h-5 text-orange-600 mr-2" />
                    Basic Information
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name *
                    </label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                        placeholder="Enter player's full name"
                        required
                    />
                    </div>

                    <div>
                    <label htmlFor="position" className="block text-sm font-medium text-gray-700 mb-2">
                        Position *
                    </label>
                    <select
                        id="position"
                        name="position"
                        value={formData.position}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                        required
                    >
                        <option value="">Select Position</option>
                        <option value="PG">Point Guard (PG)</option>
                        <option value="SG">Shooting Guard (SG)</option>
                        <option value="SF">Small Forward (SF)</option>
                        <option value="PF">Power Forward (PF)</option>
                        <option value="C">Center (C)</option>
                    </select>
                    </div>
                </div>
                </div>

                {/* Physical Attributes */}
                <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Ruler className="w-5 h-5 text-orange-600 mr-2" />
                    Physical Attributes
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                    <label htmlFor="height" className="block text-sm font-medium text-gray-700 mb-2">
                        Height *
                    </label>
                    <input
                        type="text"
                        id="height"
                        name="height"
                        value={formData.height}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                        placeholder="e.g., 6'3&quot;"
                        required
                    />
                    </div>

                    <div>
                    <label htmlFor="weight" className="block text-sm font-medium text-gray-700 mb-2">
                        Weight *
                    </label>
                    <input
                        type="text"
                        id="weight"
                        name="weight"
                        value={formData.weight}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                        placeholder="e.g., 185 lbs"
                        required
                    />
                    </div>
                </div>
                </div>

                {/* Recruiting Links */}
                <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <ExternalLink className="w-5 h-5 text-orange-600 mr-2" />
                    Recruiting Profile Links
                </h2>
                <p className="text-sm text-gray-600 mb-4">
                    Provide at least one recruiting profile link to help us gather additional information.
                </p>
                
                <div className="space-y-4">
                    <div>
                    <label htmlFor="espnLink" className="block text-sm font-medium text-gray-700 mb-2">
                        ESPN Recruiting Link
                    </label>
                    <input
                        type="url"
                        id="espnLink"
                        name="espnLink"
                        value={formData.espnLink}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                        placeholder="https://www.espn.com/college-sports/basketball/recruiting/player/..."
                    />
                    </div>

                    <div>
                    <label htmlFor="sports247Link" className="block text-sm font-medium text-gray-700 mb-2">
                        247Sports Link
                    </label>
                    <input
                        type="url"
                        id="sports247Link"
                        name="sports247Link"
                        value={formData.sports247Link}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                        placeholder="https://247sports.com/player/..."
                    />
                    </div>

                    <div>
                    <label htmlFor="rivalsLink" className="block text-sm font-medium text-gray-700 mb-2">
                        Rivals Link
                    </label>
                    <input
                        type="url"
                        id="rivalsLink"
                        name="rivalsLink"
                        value={formData.rivalsLink}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-colors"
                        placeholder="https://rivals.com/content/prospects/..."
                    />
                    </div>
                </div>
                </div>

                {/* Submit Button */}
                <div className="pt-4">
                <button
                    type="submit"
                    disabled={!isFormValid || isSubmitting}
                    className="w-full bg-orange-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-orange-700 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
                >
                    {isSubmitting ? (
                    <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Processing...
                    </>
                    ) : (
                    'Submit Player for Review'
                    )}
                </button>
                
                {!isFormValid && (
                    <p className="mt-2 text-sm text-gray-500 flex items-center">
                    <AlertCircle className="w-4 h-4 mr-1" />
                    Please fill in all required fields (marked with *)
                    </p>
                )}
                </div>
            </form>
            </div>

            {/* Additional Information */}
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-blue-800 font-semibold mb-2">What happens next?</h3>
            <ul className="text-blue-700 text-sm space-y-1">
                <li>• Our team will review the submitted information within 24-48 hours</li>
                <li>• We'll gather additional data from the provided recruiting links</li>
                <li>• Our AI will generate a comprehensive scouting report</li>
                <li>• The player will be added to our database and searchable by all users</li>
            </ul>
            </div>
        </div>
        </div>
    );
}