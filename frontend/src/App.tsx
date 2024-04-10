import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import ReportDetails from './components/ReportDetails';
import IndustryDetails from './components/IndustryDetails.tsx';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/report/:ReportNumber" element={<ReportDetails />} />
        <Route path="/industry/:subIndustryId" element={<IndustryDetails />} />
      </Routes>
    </Router>
  );
}

export default App;
