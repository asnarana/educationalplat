const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
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
  async generateQuiz(studentId, gradeLevel, topics, numQuestions = 10) {
    return this.request('/quiz/generate', {
      method: 'POST',
      body: {
        student_id: studentId,
        grade_level: gradeLevel,
        topics: topics,
        num_questions: numQuestions,
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

  // Get student history (optionally filtered by grade level)
  async getStudentHistory(studentId, gradeLevel = null) {
    let url = `/student/${studentId}/history`;
    if (gradeLevel !== null && gradeLevel !== undefined) {
      url += `?grade_level=${gradeLevel}`;
    }
    return this.request(url);
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

