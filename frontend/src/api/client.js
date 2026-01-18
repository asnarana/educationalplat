const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiClient {
  getAuthToken() {
    return localStorage.getItem('session_token');
  }

  setAuthToken(token) {
    if (token) {
      localStorage.setItem('session_token', token);
    } else {
      localStorage.removeItem('session_token');
    }
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = this.getAuthToken();
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
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

  // Authentication methods
  async login(username, password) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: { username, password },
    });
    if (response.session_token) {
      this.setAuthToken(response.session_token);
      localStorage.setItem('user', JSON.stringify(response.user));
    }
    return response;
  }

  async logout() {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } catch (e) {
      // Ignore errors on logout
    }
    this.setAuthToken(null);
    localStorage.removeItem('user');
  }

  async register(username, password, role = 'student') {
    return this.request('/auth/register', {
      method: 'POST',
      body: { username, password, role },
    });
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  getCurrentUserFromStorage() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  // Seed question bank
  async seedQuestions() {
    return this.request('/seed', { method: 'POST' });
  }

  // Clear database
  async clearDatabase() {
    return this.request('/seed/clear', { method: 'POST' });
  }

  // Generate quiz (studentId is optional if user is authenticated)
  async generateQuiz(gradeLevel, topics, numQuestions = 10, studentId = null) {
    const body = {
      grade_level: gradeLevel,
      topics: topics,
      num_questions: numQuestions,
    };
    // Only include student_id if provided (for backward compatibility)
    if (studentId) {
      body.student_id = studentId;
    }
    return this.request('/quiz/generate', {
      method: 'POST',
      body: body,
    });
  }

  // Regenerate questions for an existing quiz (for retakes)
  async regenerateQuizQuestions(quizId) {
    return this.request(`/quiz/${quizId}/regenerate`, {
      method: 'PUT',
    });
  }

  // Generate topic-specific practice quiz (studentId is optional if user is authenticated)
  async generateTopicPractice(gradeLevel, topic, numQuestions = 6, studentId = null) {
    const body = {
      grade_level: gradeLevel,
      topic: topic,
      num_questions: numQuestions,
    };
    // Only include student_id if provided (for backward compatibility)
    if (studentId) {
      body.student_id = studentId;
    }
    return this.request('/quiz/practice-topic', {
      method: 'POST',
      body: body,
    });
  }

  // Get quiz by ID
  async getQuiz(quizId) {
    return this.request(`/quiz/${quizId}`, {
      method: 'GET',
    });
  }

  // Get attempt results
  async getAttemptResults(attemptId) {
    return this.request(`/quiz/attempt/${attemptId}`, {
      method: 'GET',
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
  async getStudentHistory(studentId, gradeLevel = null, page = 1, pageSize = 10) {
    let url = `/student/${studentId}/history`;
    const params = [];
    if (gradeLevel !== null && gradeLevel !== undefined) {
      params.push(`grade_level=${gradeLevel}`);
    }
    params.push(`page=${page}`);
    params.push(`page_size=${pageSize}`);
    if (params.length > 0) {
      url += `?${params.join('&')}`;
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

  // Get available topics for a grade level and subject
  async getTopics(gradeLevel, subject = null) {
    let url = `/quiz/topics?grade_level=${gradeLevel}`;
    if (subject) {
      url += `&subject=${subject}`;
    }
    return this.request(url);
  }
}

export default new ApiClient();

