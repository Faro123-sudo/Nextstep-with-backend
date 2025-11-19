import React from 'react';
import { Modal, Button, ListGroup, Spinner } from 'react-bootstrap';
import { Briefcase, Lightbulb } from 'react-bootstrap-icons';
import './RecommendationModal.css';

const RecommendationModal = ({ show, onHide, recommendations, isLoading }) => {
  return (
    <Modal show={show} onHide={onHide} centered size="lg">
      <Modal.Header closeButton>
        <Modal.Title className="w-100 text-center fw-bold">
          <span role="img" aria-label="stars">✨</span> Your Personalized Career Recommendations <span role="img" aria-label="stars">✨</span>
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {isLoading ? (
          <div className="text-center">
            <Spinner animation="border" variant="primary" />
            <p className="mt-3">Our AI is analyzing your answers...</p>
          </div>
        ) : (
          <ListGroup variant="flush">
            {recommendations.map((rec, index) => (
              <ListGroup.Item key={index} className="recommendation-item">
                <div className="d-flex align-items-start">
                  <Briefcase size={24} className="me-3 text-primary" />
                  <div>
                    <h5 className="fw-bold mb-1">{rec.career}</h5>
                    <div className="d-flex align-items-start text-muted">
                      <Lightbulb size={20} className="me-2 mt-1 text-warning" />
                      <p className="mb-0">{rec.reason}</p>
                    </div>
                  </div>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Close
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default RecommendationModal;
