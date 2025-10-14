import React, { useState, useEffect } from "react";
import { useProfile } from "../../context/ProfileContext";
import api from "../../utils/axiosClient";
import { motion } from "framer-motion";
import { CheckCircleFill } from "react-bootstrap-icons";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import "../../components/Quiz.css";
import { submitQuizAttempt } from "../../utils/core";

export default function Quiz() {
  const { profile } = useProfile();
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showRecommendations, setShowRecommendations] = useState(false);

  useEffect(() => {
    const roleToQuizId = {
      student: 4,
      graduate: 5,
      professional: 6,
    };

    const fetchQuiz = async () => {
      if (!profile) {
        return;
      }

      const quizId = roleToQuizId[profile.user.role.toLowerCase()];

      if (!quizId) {
        setError("No quiz found for your role.");
        setLoading(false);
        return;
      }

      try {
        const response = await api.get(`/core/quizzes/${quizId}/`);
        setQuiz(response.data);
      } catch (err) {
        setError("Failed to load quiz. Please try again later.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchQuiz();
  }, [profile]);

  const handleOptionChange = (questionId, option) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionId]: option,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await submitQuizAttempt(quiz.id, selectedAnswers);
      setShowRecommendations(true);
    } catch (err) {
      setError("Failed to submit quiz. Please try again.");
      console.error(err);
    }
  };

  if (loading) {
    return <div className="text-center p-5">Loading Quiz...</div>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  if (!quiz) {
    return <div className="text-center p-5">No quiz available at the moment.</div>;
  }

  const answeredQuestions = Object.keys(selectedAnswers).length;
  const totalQuestions = quiz.questions.length;
  const progress =
    totalQuestions > 0
      ? Math.round((answeredQuestions / totalQuestions) * 100)
      : 0;

  return (
    <section className="container py-5 quiz-container">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-center mb-4 display-4 fw-bold text-primary">
          {quiz.title}
        </h1>
        <p className="text-center text-muted mb-5 fs-5">
          {quiz.description}
        </p>
      </motion.div>

      <div className="row justify-content-center">
        <div className="col-lg-7 col-md-8">
          {!showRecommendations && (
            <motion.form
              onSubmit={handleSubmit}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              {quiz.questions.map((q, index) => (
                <motion.div
                  key={q.id}
                  initial={{ opacity: 0, y: 50 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="card shadow-sm mb-4 quiz-card"
                >
                  <div className="card-body">
                    <div className="d-flex align-items-start">
                      <div className="question-number me-3">{index + 1}</div>
                      <h5 className="card-title fw-bold mb-3 flex-grow-1">
                        {q.question_text}
                      </h5>
                    </div>
                    <div className="d-grid gap-2 ps-md-5">
                      {q.options.map((option, i) => {
                        const isActive = selectedAnswers[q.id] === option;
                        return (
                          <label
                            key={i}
                            className={`btn w-100 text-start p-3 rounded-pill quiz-option-btn ${
                              isActive ? "active" : ""
                            }`}
                            htmlFor={`q${q.id}-option${i}`}
                          >
                            <input
                              type="radio"
                              className="btn-check"
                              name={`question-${q.id}`}
                              id={`q${q.id}-option${i}`}
                              value={option}
                              checked={isActive}
                              onChange={() =>
                                handleOptionChange(q.id, option)
                              }
                            />
                            <div className="d-flex justify-content-between align-items-center">
                              <span>{option}</span>
                              {isActive && (
                                <CheckCircleFill size={20} className="ms-2" />
                              )}
                            </div>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                </motion.div>
              ))}
              <button
                type="submit"
                className="btn btn-primary btn-lg w-100 mt-3"
                disabled={
                  answeredQuestions !== totalQuestions || totalQuestions === 0
                }
              >
                Submit Answers
              </button>
            </motion.form>
          )}

          {showRecommendations && (
            <div className="mt-5 text-center">
              <h3 className="fw-bold text-success mb-4">
                Quiz Submitted!
              </h3>
            </div>
          )}
        </div>

        <div className="col-lg-4 col-md-4 d-none d-md-block">
          <div className="quiz-sidebar">
            {!showRecommendations && (
              <div className="text-center mb-4">
                <div style={{ width: 150, height: 150, margin: "auto" }}>
                  <CircularProgressbar
                    value={progress}
                    text={`${progress}%`}
                    styles={buildStyles({
                      rotation: 0.25,
                      strokeLinecap: "round",
                      textSize: "16px",
                      pathTransitionDuration: 0.5,
                      pathColor: `#0d6efd`,
                      textColor: "#0d6efd",
                      trailColor: "#e9ecef",
                      backgroundColor: "#3e98c7",
                    })}
                  />
                </div>
                <p className="fw-bold mt-3">Quiz Progress</p>
              </div>
            )}
            <div className="info-card">
              <h5 className="fw-bold">User</h5>
              {profile ? (
                <p>{profile.user.username}</p>
              ) : (
                <p>Loading...</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
