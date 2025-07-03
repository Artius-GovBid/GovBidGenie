import React, { useState, useEffect } from 'react';

function Opportunities() {
  const [opportunities, setOpportunities] = useState([]);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState('');

  async function fetchOpportunities() {
    try {
      const response = await fetch('/api/v1/opportunities/');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setOpportunities(data);
    } catch (e) {
      setError(e.message);
      console.error("Failed to fetch opportunities:", e);
    }
  }

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const handleCreateLead = async (opportunityId) => {
    try {
        setNotification('');
        setError('');
        const response = await fetch('/api/v1/leads/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ opportunity_id: opportunityId }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        const lead = await response.json();
        setNotification(`Successfully created lead ${lead.id} and ADO work item ${lead.azure_devops_work_item_id}.`);
        
        // Refresh the list of opportunities
        fetchOpportunities();

    } catch (e) {
        setError(e.message);
        console.error("Failed to create lead:", e);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>Opportunity Inbox</h1>
        <p>Opportunities discovered by the Genie, ready for review.</p>
      </header>
      <main>
        {error && <div className="error-message">Error: {error}</div>}
        {notification && <div className="notification-message">{notification}</div>}
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Agency</th>
                <th>Posted Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {opportunities.length > 0 ? (
                opportunities.map((opp) => (
                  <tr key={opp.id}>
                    <td>
                      <a href={opp.url} target="_blank" rel="noopener noreferrer">
                        {opp.title}
                      </a>
                    </td>
                    <td>{opp.agency}</td>
                    <td>{opp.posted_date ? new Date(opp.posted_date).toLocaleDateString() : 'N/A'}</td>
                    <td>
                      <button onClick={() => handleCreateLead(opp.id)} className="button-primary">
                        Create Lead
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4">No new opportunities found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}

export default Opportunities; 