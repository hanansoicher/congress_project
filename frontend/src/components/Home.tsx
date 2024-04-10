import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

function Home() {
  const navigate = useNavigate();
  const [reportSearchInput, setReportSearchInput] = useState('');
  const [industrySearchInput, setIndustrySearchInput] = useState('');
  const [reportSearchResults, setReportSearchResults] = useState([]);
  const [industrySearchResults, setIndustrySearchResults] = useState([]);
  const [industries, setIndustries] = useState([]);

  useEffect(() => {
    fetch('http://localhost:3000/api/industries/all')
      .then((res) => {
        return res.json();
      })
      .then((data) => setIndustries(data.industries));
  }, []);  

  const handleReportInputChange = (event: { target: { value: string; }; }) => {
    const value = event.target.value;
    setReportSearchInput(value);
    if (value) {
      fetch(`http://localhost:3000/api/reports/search?query=${value}`)
        .then((res) => res.json())
        .then((data) => setReportSearchResults(data.results));
    } else {
      setReportSearchResults([]);
    }
  };

  const handleIndustryInputChange = (event: { target: { value: string; }; }) => {
    const value = event.target.value;
    setIndustrySearchInput(value);
    if (value) {
      fetch(`http://localhost:3000/api/industries/search?query=${value}`)
        .then((res) => res.json())
        .then((data) => setIndustrySearchResults(data.results));
    } else {
      setIndustrySearchResults([]);
    }
  };

  return (
    <div>
      <h1>Search Committee Reports or Industries</h1>
      <div className="home-container">
        <div className="search-section">
          <div className="search-container">
            <input
              type="text"
              value={reportSearchInput}
              onChange={handleReportInputChange}
              placeholder="Search reports..."
            />
          </div>
          <div className="results-container">
            {reportSearchResults && reportSearchResults.map((report: { ReportNumber: string; title: string; }) => (
              <div key={report.ReportNumber} className="result-item" onClick={() => navigate(`/report/${report.ReportNumber}`)}>
                {report.title}
              </div>
            ))}
          </div>
        </div>
        <div className="search-section">
          <div className="search-container">
            <input
              type="text"
              value={industrySearchInput}
              onChange={handleIndustryInputChange}
              placeholder="Search industries..."
            />
          </div>
          <div className="results-container">
            {industrySearchResults.length > 0
              ? industrySearchResults.map((industry: { SubIndustryId: string; SubIndustry: string; }) => (
                  <div
                    key={industry.SubIndustryId}
                    className="result-item"
                    onClick={() => navigate(`/industry/${industry.SubIndustryId}`)}
                  >
                    {industry.SubIndustry}
                  </div>
                ))
              : industries.map((industry: { SubIndustryId: string; SubIndustry: string; }) => (
                  <div
                    key={industry.SubIndustryId}
                    className="result-item"
                    onClick={() => navigate(`/industry/${industry.SubIndustryId}`)}
                  >
                    {industry.SubIndustry}
                  </div>
                ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;