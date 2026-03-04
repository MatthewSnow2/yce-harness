import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getScenarios, getScenario, createScenario, getPersonas } from '../services/api';
import ConversationTester from '../components/ConversationTester';

export default function TestConfiguration() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState(null);
  const [personas, setPersonas] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    user_persona: '',
    expected_turns: 15,
    success_criteria: []
  });
  const [criterionInput, setCriterionInput] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    const scenarioId = searchParams.get('scenario');
    if (scenarioId && scenarios.length > 0) {
      loadScenario(scenarioId);
    }
  }, [searchParams, scenarios]);

  async function loadData() {
    setLoading(true);
    try {
      const [scenariosData, personasData] = await Promise.all([
        getScenarios(),
        getPersonas()
      ]);
      setScenarios(scenariosData);
      setPersonas(personasData);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  }

  async function loadScenario(scenarioId) {
    try {
      const scenario = await getScenario(scenarioId);
      setSelectedScenario(scenario);
    } catch (err) {
      console.error('Failed to load scenario:', err);
    }
  }

  function handleInputChange(e) {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'expected_turns' ? parseInt(value, 10) : value
    }));
  }

  function addCriterion() {
    if (criterionInput.trim()) {
      setFormData(prev => ({
        ...prev,
        success_criteria: [...prev.success_criteria, criterionInput.trim()]
      }));
      setCriterionInput('');
    }
  }

  function removeCriterion(index) {
    setFormData(prev => ({
      ...prev,
      success_criteria: prev.success_criteria.filter((_, idx) => idx !== index)
    }));
  }

  async function handleCreateScenario(e) {
    e.preventDefault();

    try {
      const newScenario = await createScenario({
        ...formData,
        conversation_flow: []
      });

      setScenarios(prev => [newScenario, ...prev]);
      setSelectedScenario(newScenario);
      setShowCreateForm(false);

      // Reset form
      setFormData({
        name: '',
        description: '',
        user_persona: '',
        expected_turns: 15,
        success_criteria: []
      });
    } catch (err) {
      console.error('Failed to create scenario:', err);
      alert('Failed to create scenario');
    }
  }

  function handleTestComplete(result) {
    // Show success message
    alert(`Test completed! ${result.success ? 'PASSED' : 'FAILED'} - Score: ${result.overall_score.toFixed(1)}%`);
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
          <h1 className="text-3xl font-bold text-gray-900">Test Configuration</h1>
          <p className="text-gray-600 mt-1">Configure and execute conversation tests</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            Back to Dashboard
          </button>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            {showCreateForm ? 'Cancel' : 'Create New Scenario'}
          </button>
        </div>
      </div>

      {/* Create Scenario Form */}
      {showCreateForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Create New Test Scenario</h2>

          <form onSubmit={handleCreateScenario} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Scenario Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="e.g., Customer Support Escalation"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                required
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Describe the test scenario..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                User Persona *
              </label>
              <select
                name="user_persona"
                value={formData.user_persona}
                onChange={handleInputChange}
                required
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
                Expected Turns *
              </label>
              <input
                type="number"
                name="expected_turns"
                value={formData.expected_turns}
                onChange={handleInputChange}
                required
                min="1"
                max="50"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Success Criteria
              </label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={criterionInput}
                  onChange={(e) => setCriterionInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCriterion())}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Add a success criterion..."
                />
                <button
                  type="button"
                  onClick={addCriterion}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Add
                </button>
              </div>
              {formData.success_criteria.length > 0 && (
                <ul className="space-y-1">
                  {formData.success_criteria.map((criterion, idx) => (
                    <li key={idx} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                      <span className="text-sm text-gray-700">{criterion}</span>
                      <button
                        type="button"
                        onClick={() => removeCriterion(idx)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Create Scenario
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Scenario Selection */}
      {!showCreateForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Select Test Scenario</h2>

          <select
            value={selectedScenario?.scenario_id || ''}
            onChange={(e) => {
              const scenario = scenarios.find(s => s.scenario_id === e.target.value);
              setSelectedScenario(scenario);
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Choose a scenario...</option>
            {scenarios.map((scenario) => (
              <option key={scenario.scenario_id} value={scenario.scenario_id}>
                {scenario.name}
              </option>
            ))}
          </select>

          {selectedScenario && (
            <div className="mt-4 p-4 bg-gray-50 rounded-md">
              <h3 className="font-semibold text-gray-900">{selectedScenario.name}</h3>
              <p className="text-sm text-gray-600 mt-1">{selectedScenario.description}</p>
              <div className="mt-2 text-xs text-gray-500">
                <span>Persona: {selectedScenario.user_persona.replace(/_/g, ' ')}</span>
                <span className="mx-2">•</span>
                <span>Expected Turns: {selectedScenario.expected_turns}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Conversation Tester */}
      {!showCreateForm && (
        <ConversationTester
          scenario={selectedScenario}
          onComplete={handleTestComplete}
        />
      )}
    </div>
  );
}
