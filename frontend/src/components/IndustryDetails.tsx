import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

type Report = {
  ReportNumber: string;
  title: string;
  similarityScore: number;
};

function IndustryDetails() {
  const { SubIndustryId } = useParams();
  const [industry, setIndustry] = useState(null);
  const [reports, setReports] = useState<Report[]>([]);

  useEffect(() => {
    // Fetch industry details
    fetch(`http://localhost:3000/api/industries/${SubIndustryId}`)
      .then((res) => res.json())
      .then((data) => setIndustry(data.industry));

    // Fetch reports for this industry
    fetch(`http://localhost:3000/api/reports/by-industry/${SubIndustryId}`)
      .then((res) => res.json())
      .then((data) => setReports(data.reports));
  }, [SubIndustryId]);

  return (
    <div>
      <h2>Industry Details: {SubIndustryId}</h2>
      {industry && (
        <div>
          <h3>Overview</h3>
          <p>{industry.summarized_description}</p> {/* Use the summarized_description field */}
        </div>
      )}
      <h3>Related Reports</h3>
      <div>
        {reports.map((report) => (
          <div key={report.ReportNumber} className="report-card">
            <Link to={`/report/${report.ReportNumber}`}>
              <h4>{report.title}</h4>
              <p>Report Number: {report.ReportNumber}</p>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

export default IndustryDetails;
