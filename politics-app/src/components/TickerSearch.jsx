import { useState } from 'react';


function TickerSearch() {
    const [ticker, setTicker] = useState('');
    const [reports, setReports] = useState([]);

    const handleSearch = async () => {
        const response = await fetch(`/search/${ticker}`);
        const data = await response.json();
        setReports(data);
    };

    return (
        <div>
            <input 
                type="text" 
                value={ticker} 
                onChange={(e) => setTicker(e.target.value)} 
                placeholder="Enter ticker symbol"
            />
            <button onClick={handleSearch}>Search</button>

            {reports.length > 0 && (
        <div>
            {reports.map((report, index) => (
                <div key={index} className="report">
                    <h3>{report.title}</h3>
                    {/* Add other report details here */}
                    <p>Report ID: {report.reportId}</p>
                    {/* You can add more details as per your report structure */}
                </div>
            ))}
        </div>
        )}
    </div>
)}

export default TickerSearch;