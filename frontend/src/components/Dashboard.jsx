import React, { useState, useEffect } from 'react';
import '../App.css';

function Dashboard() {
  const [leads, setLeads] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchLeads() {
      try {
        // Use an absolute path to the API endpoint
        const response = await fetch('/api/v1/dashboard/leads');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setLeads(data);
      } catch (e) {
        setError(e.message);
        console.error("Failed to fetch leads:", e);
      }
    }

    fetchLeads();
  }, []);

  const getAdoWorkItemUrl = (id) => {
    // This is a placeholder. You'll need to replace this with your actual Azure DevOps organization URL.
    const orgUrl = "https://dev.azure.com/artiusit"; 
    return `${orgUrl}/_workitems/edit/${id}`;
  };

  return (
    <div className="container">
      <header>
        <h1>GovBidGenie Dashboard</h1>
      </header>
      <main>
        {error && <div className="error-message">Error: {error}</div>}
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Lead ID</th>
                <th>Opportunity Title</th>
                <th>Agency</th>
                <th>Status</th>
                <th>ADO Work Item</th>
              </tr>
            </thead>
            <tbody>
              {leads.length > 0 ? (
                leads.map((lead) => (
                  <tr key={lead.id}>
                    <td>{lead.id}</td>
                    <td>
                      <a href={lead.opportunity.url} target="_blank" rel="noopener noreferrer">
                        {lead.opportunity.title}
                      </a>
                    </td>
                    <td>{lead.opportunity.agency}</td>
                    <td>{lead.status}</td>
                    <td>
                      {lead.azure_devops_work_item_id ? (
                        <a href={getAdoWorkItemUrl(lead.azure_devops_work_item_id)} target="_blank" rel="noopener noreferrer">
                          {lead.azure_devops_work_item_id}
                        </a>
                      ) : (
                        'N/A'
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5">No leads found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}

export default Dashboard
