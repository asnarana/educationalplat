// Use relative URL if VITE_API_URL is a relative path, otherwise use full URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE_URL = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;

class ApiClient {
  async request(endpoint, options = {}) {
    // Handle both absolute URLs (http://...) and relative paths (/api)
    const endpointPath = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${API_BASE_URL}${endpointPath}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
      }

      // Handle binary responses (like TTS)
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('audio')) {
        return response.blob();
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Seed question bank
  async seedQuestions() {
    return this.request('/seed', { method: 'POST' });
  }

  // Clear database
  async clearDatabase() {
    return this.request('/seed/clear', { method: 'POST' });
  }

  // Generate quiz
  // useAdaptive: true = use 70/30 split with weak topics (for retakes), false = ignore weak topics, 2 per topic (for home page)
  async generateQuiz(studentId, gradeLevel, topics, numQuestions = 10, useAdaptive = false) {
    return this.request('/quiz/generate', {
      method: 'POST',
      body: {
        student_id: studentId,
        grade_level: gradeLevel,
        topics: topics,
        num_questions: numQuestions,
        use_adaptive: useAdaptive,
      },
    });
  }

  // Generate topic-specific practice quiz
  async generateTopicPractice(studentId, gradeLevel, topic, numQuestions = 6) {
    return this.request('/quiz/practice-topic', {
      method: 'POST',
      body: {
        student_id: studentId,
        grade_level: gradeLevel,
        topic: topic,
        num_questions: numQuestions,
      },
    });
  }

  // Submit quiz
  async submitQuiz(quizId, answers) {
    return this.request(`/quiz/${quizId}/submit`, {
      method: 'POST',
      body: { answers },
    });
  }

  // Get student history
  async getStudentHistory(studentId) {
    return this.request(`/student/${studentId}/history`);
  }

  // Get feedback
  async getFeedback(attemptId) {
    return this.request(`/attempt/${attemptId}/feedback`, {
      method: 'POST',
    });
  }

  // Text to speech
  async textToSpeech(text, voice = 'default') {
    return this.request('/tts', {
      method: 'POST',
      body: { text, voice },
    });
  }
}

export default new ApiClient();

