const express = require('express');
const cors = require('cors');
const router = require('./routes');

const app = express();
app.use(cors())
app.use(express.json());

const port = 3000;

app.use('/api', router);

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
