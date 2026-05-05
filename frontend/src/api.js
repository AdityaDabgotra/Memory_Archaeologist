import axios from 'axios';

// const BASE = process.env.REACT_APP_BACKEND_URL;
const BASE = 'http://localhost:8000';

export const queryMemories = async (query) => {
  const res = await axios.post(`${BASE}/query`, { query });
  return res.data;
};

export const getConcepts = async () => {
  const res = await axios.get(`${BASE}/concepts`);
  return res.data;
};

export const getStats = async () => {
  const res = await axios.get(`${BASE}/stats`);
  return res.data;
};

export const getConceptTimeline = async (concept) => {
  const res = await axios.post(`${BASE}/concepts/timeline`, { concept });
  return res.data;
};

export const getPersonTimeline = async (person) => {
  const res = await axios.post(`${BASE}/people/timeline`, { person });
  return res.data;
};