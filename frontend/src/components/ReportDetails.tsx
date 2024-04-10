import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

function ReportDetails() {
  const { ReportNumber } = useParams();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    fetch(`/api/reports/${ReportNumber}`)
      .then((res) => res.json())
      .then((data) => setReport(data));
  }, [ReportNumber]);

  if (!report) return <div>Loading...</div>;

  return (
    <div>
      <h2>{report.title}</h2>
      <p>{report.committee}</p>
      <p>Industry: {report.industry}</p>
    </div>
  );
}

export default ReportDetails;
