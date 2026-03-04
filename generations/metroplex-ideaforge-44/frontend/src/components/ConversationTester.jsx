import React, { useState, useEffect } from 'react';
import { executeScenario, getPersonas } from '../services/api';

export default function ConversationTester({ scenario, onComplete }) {
  const [personas, setPersonas] = useState([]);
  const [selectedPersona, setSelectedPersona] = useState('');
  const [numTurns, setNumTurns] = useState(15);
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPersonas();
  }, []);

  useEffect(() => {
    if (scenario) {
      setSelectedPersona(scenario.user_persona);
      setNumTurns(scenario.expected_turns);
    }
  }, [scenario]);

  async function loadPersonas() {
    try {
      const data = await getPersonas();
      setPersonas(data);
    } catch (err) {
      console.error('Failed to load personas:', err);
    }
  }

  async function handleExecute() {
    if (!scenario) return;

    setIsExecuting(true);
    setError(null);
    setResult(null);

    try {
      const executionResult = await executeScenario(scenario.scenario_id, numTurns);
      setResult(executionResult);
      if (onComplete) {
        onComplete(executionResult);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsExecuting(false);
    }
  }

  if (!scenario) {
    return (
      <div className="text-center py-12 text-gray-500">
        Select a scenario to begin testing
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Configuration Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Test Configuration</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scenario
            </label>
            <div className="text-sm text-gray-900">{scenario.name}</div>
            <div className="text-xs text-gray-500 mt-1">{scenario.description}</div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              User Persona
            </label>
            <select
              value={selectedPersona}
              onChange={(e) => setSelectedPersona(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a persona...</option>
              {personas.map((persona) => (
                <option key={persona.persona_id} value={persona.persona_id}>
                  {persona.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Turns
            </label>
            <input
              type="number"
              value={numTurns}
              onChange={(e) => setNumTurns(parseInt(e.target.value, 10))}
              min="1"
              max="50"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <button
            onClick={handleExecute}
            disabled={isExecuting || !selectedPersona}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isExecuting ? 'Running Test...' : 'Execute Test'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 text-sm">{error}</p>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-4">
          {/* Summary Card */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Test Results</h3>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Status</div>
                <div className={`text-lg font-semibold ${result.success ? 'text-green-600' : 'text-red-600'}`}>
                  {result.success ? 'PASSED' : 'FAILED'}
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Overall Score</div>
                <div className="text-lg font-semibold text-gray-900">
                  {result.overall_score?.toFixed(1)}%
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Context Score</div>
                <div className="text-lg font-semibold text-gray-900">
                  {result.context_score?.toFixed(1)}%
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Total Turns</div>
                <div className="text-lg font-semibold text-gray-900">
                  {result.turns?.length || 0}
                </div>
              </div>
            </div>

            {/* Success Criteria */}
            {scenario.success_criteria && scenario.success_criteria.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-semibold mb-2">Success Criteria</h4>
                <ul className="space-y-1">
                  {scenario.success_criteria.map((criterion, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      {criterion}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Conversation Turns */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Conversation Turns</h3>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              {result.turns && result.turns.map((turn) => (
                <div
                  key={turn.turn_id}
                  className={`border-l-4 pl-4 py-2 ${
                    turn.context_maintained ? 'border-green-500' : 'border-red-500'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-semibold text-sm text-gray-900">
                      Turn {turn.turn_id}
                    </div>
                    <div className="flex items-center gap-3 text-xs">
                      <span className={`px-2 py-1 rounded ${
                        turn.context_maintained ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {turn.context_maintained ? 'Context OK' : 'Context Lost'}
                      </span>
                      <span className="text-gray-500">
                        {turn.response_time_ms}ms
                      </span>
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="font-medium text-blue-600">User:</span>
                      <span className="ml-2 text-gray-700">{turn.user_input}</span>
                    </div>

                    <div>
                      <span className="font-medium text-purple-600">Agent:</span>
                      <span className="ml-2 text-gray-700">{turn.agent_response}</span>
                    </div>

                    <div className="flex gap-4 text-xs text-gray-500">
                      {turn.intent_detected && (
                        <span>
                          Intent: <span className="font-medium">{turn.intent_detected}</span>
                        </span>
                      )}
                      <span>
                        Confidence: <span className="font-medium">{(turn.confidence_score * 100).toFixed(1)}%</span>
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
