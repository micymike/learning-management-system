/* eslint-disable no-undef */
const express = require("express");
const bodyParser = require("body-parser");
const fs = require("fs");
const cors = require("cors");
const app = express();
const port = 5000;

// Enable CORS and parse JSON request bodies
app.use(cors());
app.use(bodyParser.json());

// Endpoint to get blog data
app.get("/api/blogs", (req, res) => {
  const filePath = "../src/assets/blogsData.json";
  // Read the blog data from the JSON file
  fs.readFile(filePath, (err, data) => {
    if (err) {
      // If there's an error reading the file, return a 500 error
      return res.status(500).send("Error reading file");
    }
    const blogs = JSON.parse(data);
    // Check if the data is an array
    if (!Array.isArray(blogs)) {
      // If the data is not an array, return a 500 error
      return res.status(500).send("Invalid data format");
    }
    // Return the blog data as JSON
    res.json(blogs);
  });
});

// Endpoint to save new blog data
app.post("/api/blogs", (req, res) => {
  const blogData = req.body;
  const filePath = "../src/assets/blogsData.json";

  // Read the existing blog data from the JSON file
  fs.readFile(filePath, (err, data) => {
    if (err) {
      // If the file doesn't exist, create a new one with the new blog data
      if (err.code === "ENOENT") {
        fs.writeFile(filePath, JSON.stringify([blogData], null, 2), (err) => {
          if (err) {
            // If there's an error writing the file, return a 500 error
            return res.status(500).send("Error writing file");
          }
          // Return a success message
          res.status(200).send("Blog data saved successfully");
        });
      } else {
        // If there's another error reading the file, return a 500 error
        return res.status(500).send("Error reading file");
      }
    } else {
      // If the file exists, parse the existing data and add the new blog data
      const existingData = JSON.parse(data);
      existingData.push(blogData);

      // Write the updated data to the file
      fs.writeFile(filePath, JSON.stringify(existingData, null, 2), (err) => {
        if (err) {
          // If there's an error writing the file, return a 500 error
          return res.status(500).send("Error writing file");
        }
        // Return a success message
        res.status(200).send("Blog data saved successfully");
      });
    }
  });
});

// Start the server and listen on the specified port
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
