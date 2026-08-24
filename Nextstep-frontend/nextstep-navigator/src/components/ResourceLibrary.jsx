import React, { useState, useMemo, useEffect } from "react";
import data from "../data/careerData.json";
import './ResourceLibrary.css';
import { FaSearch, FaFileAlt, FaBookOpen, FaChalkboardTeacher, FaFileDownload, FaRobot } from 'react-icons/fa';
import api from "../utils/axiosClient";

const resourceTypes = ["All", "Article", "E-book", "Webinar", "Template"];

const getIconForType = (type) => {
  switch (type) {
    case "Article":
      return <FaFileAlt className="resource-icon" />;
    case "E-book":
      return <FaBookOpen className="resource-icon" />;
    case "Webinar":
      return <FaChalkboardTeacher className="resource-icon" />;
    case "Template":
      return <FaFileDownload className="resource-icon" />;
    default:
      return null;
  }
};

export default function ResourceLibrary() {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeFilter, setActiveFilter] = useState("All");
  const [resources, setResources] = useState([]);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSearching, setAiSearching] = useState(false);
  const [infoMessage, setInfoMessage] = useState("");

  const allResources = useMemo(() => {
    return [
      ...data.resourceLibrary.articles,
      ...data.resourceLibrary.ebooks,
      ...data.resourceLibrary.webinars,
      ...(data.resourceLibrary.templates || []),
    ];
  }, []);

  const normaliseType = (type) => {
    const value = (type || "").toLowerCase();
    if (value === "article") return "Article";
    if (value === "e-book" || value === "ebook") return "E-book";
    if (value === "webinar") return "Webinar";
    if (value === "template") return "Template";
    return "Article";
  };

  const mapResource = (resource, fallbackId) => ({
    id: resource.id || fallbackId,
    type: normaliseType(resource.type),
    title: resource.title || "Untitled Resource",
    description: resource.description || "",
    url: resource.url || "#",
    tags: Array.isArray(resource.tags) ? resource.tags : [],
  });

  const mergeResources = (base, incoming) => {
    const merged = [...base];
    const seen = new Set(base.map((item) => (item.title || "").trim().toLowerCase()));

    incoming.forEach((item, idx) => {
      const mapped = mapResource(item, `ai-${Date.now()}-${idx}`);
      const key = mapped.title.trim().toLowerCase();
      if (key && !seen.has(key)) {
        seen.add(key);
        merged.push(mapped);
      }
    });

    return merged;
  };

  useEffect(() => {
    setResources(allResources.map((item, idx) => mapResource(item, `local-${idx}`)));
  }, [allResources]);

  const generateAiResources = async (topic = "career development") => {
    setAiLoading(true);
    setInfoMessage("");

    // Get user role from auth context for personalized resources
    const userType = user?.role || 'student';

    try {
      const res = await api.post("/ai/resources/generate/", {
        topic,
        limit: 12,
        userType,
      });

      const aiResources = Array.isArray(res.data?.resources) ? res.data.resources : [];
      if (aiResources.length > 0) {
        setResources((prev) => mergeResources(prev, aiResources));
        setInfoMessage(`AI added ${aiResources.length} realistic resources to your library.`);
      }
    } catch (error) {
      console.error("AI resource generation failed:", error);
      setInfoMessage("AI generation unavailable. Showing saved resources.");
    } finally {
      setAiLoading(false);
    }
  };

  useEffect(() => {
    generateAiResources();
  }, []);

  const searchWithAi = async () => {
    if (!searchTerm.trim()) return;

    setAiSearching(true);
    setInfoMessage("");

    // Get user role for personalized search results
    const userType = user?.role || 'student';

    try {
      const res = await api.post("/ai/resources/search/", {
        query: searchTerm.trim(),
        limit: 8,
        userType,
      });

      const aiResults = Array.isArray(res.data?.resources) ? res.data.resources : [];
      if (aiResults.length > 0) {
        setResources((prev) => mergeResources(prev, aiResults));
        setInfoMessage(`AI found ${aiResults.length} additional resources for "${searchTerm}".`);
      } else {
        setInfoMessage("AI found no additional resources for this query.");
      }
    } catch (error) {
      console.error("AI resource search failed:", error);
      setInfoMessage("AI search failed. Try again in a moment.");
    } finally {
      setAiSearching(false);
    }
  };

  const filteredResources = useMemo(() => {
    return resources.filter(resource => {
      const matchesFilter = activeFilter === "All" || resource.type === activeFilter;
      const searchValue = searchTerm.toLowerCase();
      const matchesSearch =
        searchTerm === "" ||
        resource.title.toLowerCase().includes(searchValue) ||
        resource.description.toLowerCase().includes(searchValue) ||
        (resource.tags || []).some((tag) => String(tag).toLowerCase().includes(searchValue));
      return matchesFilter && matchesSearch;
    });
  }, [resources, activeFilter, searchTerm]);

  return (
    <section className="resource-library-section container py-5">
      <div className="text-center mb-5" data-aos="fade-down">
        <h1 className="display-4 fw-bold text-primary">Resource Library 📚</h1>
        <p className="lead text-muted" data-aos-delay="100">Your one-stop hub for career-enhancing articles, e-books, and tools.</p>
      </div>

      <div className="controls-wrapper mb-5 p-4 rounded-4 shadow-sm" data-aos="fade-up" data-aos-delay="200">
        <div className="row g-3 align-items-center">
          <div className="col-lg-5 col-md-12">
            <div className="input-group">
              <span className="input-group-text"><FaSearch /></span>
              <input
                type="text"
                className="form-control"
                placeholder="Search resources..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <button
                type="button"
                className="btn btn-outline-primary"
                onClick={searchWithAi}
                disabled={aiSearching || !searchTerm.trim()}
              >
                {aiSearching ? "Searching..." : "AI Search"}
              </button>
            </div>
          </div>
          <div className="col-lg-7 col-md-12">
            <div className="filter-buttons d-flex flex-wrap justify-content-center justify-content-lg-start gap-2">
              {resourceTypes.map(type => (
                <button
                  key={type}
                  className={`btn btn-sm rounded-pill ${activeFilter === type ? 'btn-primary' : 'btn-outline-secondary'}`}
                  onClick={() => setActiveFilter(type)}
                >
                  {type}s
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="d-flex flex-wrap justify-content-center gap-2 mb-4" data-aos="fade-up" data-aos-delay="250">
        <button
          type="button"
          className="btn btn-primary rounded-pill"
          onClick={() => generateAiResources(searchTerm.trim() || "career development")}
          disabled={aiLoading}
        >
          <FaRobot className="me-2" />
          {aiLoading ? "Generating realistic resources..." : "Generate AI Resource Library"}
        </button>
        {infoMessage ? <span className="small text-muted align-self-center">{infoMessage}</span> : null}
      </div>

      <div className="row g-4" data-aos="fade-up" data-aos-delay="300">
        {filteredResources.length > 0 ? (
          filteredResources.map((resource, idx) => (
            <div key={resource.id} className="col-lg-4 col-md-6" data-aos="fade-up" data-aos-delay={idx * 50}>
              <div className="resource-card card h-100 shadow-sm border-0">
                <div className="card-body d-flex flex-column">
                  <div className="d-flex align-items-start mb-3">
                    {getIconForType(resource.type)}
                    <div className="flex-grow-1">
                      <h5 className="card-title fw-bold mb-1">{resource.title}</h5>
                      <span className="badge bg-primary-subtle text-primary-emphasis rounded-pill">{resource.type}</span>
                    </div>
                  </div>
                  <p className="card-text text-muted small flex-grow-1">{resource.description}</p>
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-outline-primary btn-sm mt-auto stretched-link"
                  >
                    {resource.type === 'Webinar' ? 'Watch Now' : 'Access Resource'}
                  </a>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="col-12 text-center py-5" data-aos="zoom-in">
            <h4 className="text-muted">No resources found.</h4>
            <p className="text-muted">Try adjusting your search or filter.</p>
          </div>
        )}
      </div>
    </section>
  );
}