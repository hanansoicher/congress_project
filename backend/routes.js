const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const router = express.Router();

// Connect to the SQLite database for reports
const dbReports = new sqlite3.Database('../data/reports_db.sqlite', sqlite3.OPEN_READONLY, (err) => {
  if (err) {
    console.error('Error connecting to the reports database:', err.message);
  } else {
    console.log('Connected to the reports SQLite database.');
  }
});

// Connect to the SQLite database for industries
const dbIndustries = new sqlite3.Database('../data/industry_db.sqlite', sqlite3.OPEN_READONLY, (err) => {
  if (err) {
    console.error('Error connecting to the industries database:', err.message);
  } else {
    console.log('Connected to the industries SQLite database.');
  }
});

// API endpoint to get all committee reports
router.get('/reports', (req, res) => {
  const sql = 'SELECT * FROM committee_reports';
  dbReports.all(sql, [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({
      message: 'Success',
      data: rows
    });
  });
});

// API endpoint to get a specific committee report by report number
router.get('/reports/:ReportNumber', (req, res) => {
  const ReportNumber = req.params.ReportNumber;
  const sql = 'SELECT * FROM committee_reports WHERE ReportNumber = ?';
  dbReports.get(sql, [ReportNumber], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    if (row) {
      res.json({
        message: 'Success',
        data: row
      });
    } else {
      res.status(404).json({ error: 'Report not found' });
    }
  });
});

// API endpoint to search committee reports by title or text
router.get('/reports/search', (req, res) => {
  const query = req.query.query;
  const sql = "SELECT * FROM committee_reports WHERE Title LIKE ? OR report_text LIKE ?";
  dbReports.all(sql, [`%${query}%`, `%${query}%`], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({
      message: 'Success',
      results: rows
    });
  });
});

// API endpoint to get all industries
router.get('/industries/all', (req, res) => {
  const sql = 'SELECT * FROM industries';
  dbIndustries.all(sql, [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({
      message: 'Success',
      industries: rows
    });
  });
});

router.get('/industries/search', (req, res) => {
  const query = req.query.query;
  const sql = "SELECT * FROM industries WHERE SubIndustry LIKE ?";
  dbIndustries.all(sql, [`%${query}%`], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({
      message: 'Success',
      results: rows
    });
  });
});

// API endpoint to get industry details by SubIndustryId
router.get('/industries/:SubIndustryId', (req, res) => {
  const id = req.params.id;
  const sql = "SELECT * FROM industries WHERE SubIndustryId = ?";
  dbIndustries.get(sql, [SubIndustryId], (err, row) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    if (row) {
      res.json({
        message: 'Success',
        industry: row
      });
    } else {
      res.status(404).json({ error: 'Industry not found' });
    }
  });
});

// API endpoint to get reports by industry
router.get('/reports/by-industry/:SubIndustryId', (req, res) => {
  const SubIndustryId = req.params.SubIndustryId;
  const sql = "SELECT * FROM report_classifications WHERE ClassifiedSubIndustries LIKE ?";
  dbReports.all(sql, [`%${SubIndustryId}%`], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json({
      message: 'Success',
      reports: rows
    });
  });
});


module.exports = router;
