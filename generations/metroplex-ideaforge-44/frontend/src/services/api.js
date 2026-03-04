/**
 * API service for VoiceAgent QA Platform
 */

const API_BASE_URL = '/api';

/**
 * Fetch all test scenarios
 */
export async function getScenarios() {
  const response = await fetch(`${API_BASE_URL}/scenarios`);
  if (!response.ok) {
    throw new Error('Failed to fetch scenarios');
  }
  return response.json();
}

/**
 * Get a specific scenario
 */
export async function getScenario(scenarioId) {
  const response = await fetch(`${API_BASE_URL}/scenarios/${scenarioId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch scenario');
  }
  return response.json();
}

/**
 * Create a new test scenario
 */
export async function createScenario(scenarioData) {
  const response = await fetch(`${API_BASE_URL}/scenarios`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(scenarioData),
  });
  if (!response.ok) {
    throw new Error('Failed to create scenario');
  }
  return response.json();
}

/**
 * Execute a conversation test
 */
export async function executeScenario(scenarioId, numTurns = null) {
  const response = await fetch(`${API_BASE_URL}/scenarios/${scenarioId}/execute`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ scenario_id: scenarioId, num_turns: numTurns }),
  });
  if (!response.ok) {
    throw new Error('Failed to execute scenario');
  }
  return response.json();
}

/**
 * Get conversation results
 */
export async function getConversation(conversationId) {
  const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch conversation');
  }
  return response.json();
}

/**
 * Get all conversations
 */
export async function getConversations() {
  const response = await fetch(`${API_BASE_URL}/conversations`);
  if (!response.ok) {
    throw new Error('Failed to fetch conversations');
  }
  return response.json();
}

/**
 * Fetch all user personas
 */
export async function getPersonas() {
  const response = await fetch(`${API_BASE_URL}/personas`);
  if (!response.ok) {
    throw new Error('Failed to fetch personas');
  }
  return response.json();
}

/**
 * Get a specific persona
 */
export async function getPersona(personaId) {
  const response = await fetch(`${API_BASE_URL}/personas/${personaId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch persona');
  }
  return response.json();
}
