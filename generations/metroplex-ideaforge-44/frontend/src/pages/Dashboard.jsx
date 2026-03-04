import React, { useState, useEffect } from 'react';
import { getScenarios, getConversations } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [scenarios, setScenarios] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const [scenariosData, conversationsData] = await Promise.all([
        getScenarios(),
        getConversations()
      ]);
      setScenarios(scenariosData);
      setConversations(conversationsData.slice(0, 10)); // Show last 10
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Conversation Flow Testing Platform</p>
        </div>
        <button
          onClick={() => navigate('/test-configuration')}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          New Test Scenario
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Total Scenarios</div>
          <div className="text-3xl font-bold text-gray-900">{scenarios.length}</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Total Tests Run</div>
          <div className="text-3xl font-bold text-gray-900">{conversations.length}</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-1">Success Rate</div>
          <div className="text-3xl font-bold text-gray-900">
            {conversations.length > 0
              ? ((conversations.filter(c => c.success).length / conversations.length) * 100).toFixed(0)
              : 0}%
          </div>
        </div>
      </div>

      {/* Test Scenarios */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Test Scenarios</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {scenarios.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No scenarios yet. Create your first test scenario to get started.
            </div>
          ) : (
            scenarios.map((scenario) => (
              <div
                key={scenario.scenario_id}
                className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => navigate(`/test-configuration?scenario=${scenario.scenario_id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{scenario.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{scenario.description}</p>
                    <div className="flex gap-4 mt-2 text-xs text-gray-500">
                      <span>Persona: {scenario.user_persona.replace(/_/g, ' ')}</span>
                      <span>Expected Turns: {scenario.expected_turns}</span>
                      <span>Created: {formatDate(scenario.created_at)}</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/test-configuration?scenario=${scenario.scenario_id}`);
                    }}
                    className="ml-4 px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                  >
                    Run Test
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Recent Test Results */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold">Recent Test Results</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {conversations.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No test results yet. Run a test scenario to see results here.
            </div>
          ) : (
            conversations.map((conversation) => (
              <div
                key={conversation.conversation_id}
                className="p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-1 text-xs rounded font-medium ${
                        conversation.success
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {conversation.success ? 'PASSED' : 'FAILED'}
                      </span>
                      <span className="font-medium text-gray-900">
                        {conversation.scenario_id}
                      </span>
                    </div>
                    <div className="flex gap-4 mt-2 text-sm text-gray-600">
                      <span>Turns: {conversation.turns?.length || 0}</span>
                      <span>Overall Score: {conversation.overall_score?.toFixed(1)}%</span>
                      <span>Context Score: {conversation.context_score?.toFixed(1)}%</span>
                      <span>Started: {formatDate(conversation.started_at)}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
