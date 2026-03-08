import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, Calendar, ExternalLink, ShieldCheck, Zap, BarChart3, Clock, Mail } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const App = () => {
  const [data, setData] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [searchKeywords, setSearchKeywords] = useState('');

  const fetchProfile = async () => {
    try {
      const response = await axios.get('http://localhost:8011/profile');
      setProfile(response.data);
    } catch (err) {
      console.error('Failed to fetch profile', err);
    }
  };

  const discoverJobs = async (keywords = '') => {
    setLoading(true);
    setError(null);
    try {
      const url = keywords
        ? `http://localhost:8011/discover?keywords=${encodeURIComponent(keywords)}`
        : `http://localhost:8011/discover`;
      const response = await axios.get(url);
      setData(response.data);
    } catch (err) {
      setError('Failed to connect to the discovery agent. Ensure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8011/profile/update', profile);
      setIsEditing(false);
      discoverJobs(); // Refresh jobs with new profile
    } catch (err) {
      setError('Failed to update profile.');
    }
  };

  const handleResumeUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) {
      console.log("No file selected");
      return;
    }

    console.log("File selected:", file.name, file.size, file.type);

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setError(null);
    try {
      console.log("Sending request to http://localhost:8011/profile/upload-resume");
      const response = await axios.post('http://localhost:8011/profile/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      console.log("Upload response:", response.data);
      setProfile(response.data.profile);
      alert('Resume parsed! Profile updated with extracted skills.');
      discoverJobs(); // Refresh jobs
    } catch (err) {
      console.error("Upload error details:", err);
      if (err.response) {
        console.error("Response data:", err.response.data);
        console.error("Response status:", err.response.status);
      }
      setError(err.response?.data?.detail || 'Failed to upload resume. Ensure backend is running.');
    } finally {
      setUploading(false);
      // Clear the input value so the same file can be uploaded again if needed
      e.target.value = '';
    }
  };

  const [isNavigating, setIsNavigating] = useState(false);

  const handleApply = async (internship) => {
    const keywords = searchKeywords || profile?.target_roles?.[0] || 'internship';
    const company = internship.company_name.toLowerCase();
    let finalUrl = internship.application_link;

    // Show automation feedback
    setIsNavigating(true);

    // Smart Redirection Logic
    const platformTemplates = {
      google: `https://www.google.com/search?q=${encodeURIComponent(keywords)}+internship+at+google+careers`,
      microsoft: `https://careers.microsoft.com/us/en/search-results?keywords=${encodeURIComponent(keywords)}`,
      amazon: `https://www.amazon.jobs/en/search?base_query=${encodeURIComponent(keywords)}&loc_query=India`,
      linkedin: `https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(keywords)}&location=India`,
      indeed: `https://in.indeed.com/jobs?q=${encodeURIComponent(keywords)}&l=India`,
      glassdoor: `https://www.glassdoor.co.in/Job/india-${keywords.toLowerCase().replace(/\s+/g, '-')}-jobs-SRCH_IL.0,5_IN115_KO6,${6 + keywords.length}.htm`,
      internshala: `https://internshala.com/internships/keywords-${encodeURIComponent(keywords)}`,
      naukri: `https://www.naukri.com/${keywords.toLowerCase().replace(/\s+/g, '-')}-internship-in-india`,
    };

    // Check templates
    for (const [key, template] of Object.entries(platformTemplates)) {
      if (company.includes(key)) {
        finalUrl = template;
        break;
      }
    }

    // Default Fallback: Smart Site Search
    if (finalUrl === internship.application_link && (searchKeywords || profile?.target_roles?.[0])) {
      const activeKeywords = searchKeywords || profile?.target_roles?.[0];

      // Clean up the query: Avoid "Intern internship" redundancy
      let cleanQuery = activeKeywords.trim();
      if (!cleanQuery.toLowerCase().includes('intern')) {
        cleanQuery += ' internship';
      }

      try {
        const urlObj = new URL(finalUrl);
        const path = urlObj.pathname;
        const isGeneric = path === '/' ||
          path.match(/^\/(careers|jobs|internships|students)\/?$/i) ||
          (finalUrl.length < 40 && !path.includes('view') && !path.includes('id='));

        if (isGeneric) {
          finalUrl = `https://www.google.com/search?q=site:${urlObj.hostname} ${encodeURIComponent(cleanQuery)}`;
        }
      } catch (e) {
        console.error("Redirection error:", e);
      }
    }

    setTimeout(() => {
      window.open(finalUrl, '_blank');
      setIsNavigating(false);
    }, 1500);
  };

  const triggerScan = async () => {
    setLoading(true);
    try {
      await axios.post('http://localhost:8011/scan/now');
      alert("Background scan triggered! You'll receive an email summary once it's complete.");
    } catch (err) {
      setError('Failed to trigger scan.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
    discoverJobs();
  }, []);

  return (
    <div className="app-container" style={{ position: 'relative' }}>
      <AnimatePresence>
        {isNavigating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(13, 17, 23, 0.9)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 9999,
              backdropFilter: 'blur(8px)'
            }}
          >
            <div className="spinner" style={{ width: '60px', height: '60px' }}></div>
            <motion.h2
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              style={{ marginTop: '2rem', fontSize: '1.5rem', fontWeight: 'bold' }}
            >
              Agent is navigating to career portal...
            </motion.h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>Automatically searching for "{searchKeywords || 'internships'}" on the target site</p>
          </motion.div>
        )}
      </AnimatePresence>
      <header style={{ padding: '2rem 1rem', textAlign: 'center' }}>
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ fontSize: '2.5rem', fontWeight: '800', background: 'linear-gradient(90deg, #58a6ff, #bc8cff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
        >
          AI Internship Discovery Agent
        </motion.h1>
        <p style={{ color: 'var(--text-secondary)' }}>Autonomous discovery engine for 4th Year MSc Data Science students</p>
      </header>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: '1rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2.5fr', gap: '2rem' }}>

          {/* Sidebar / Profile & Stats */}
          <aside>
            <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
              <h3><ShieldCheck size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} /> Candidate Profile</h3>

              {!profile ? (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Loading profile data...</p>
              ) : !isEditing ? (
                <>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontWeight: '600', marginBottom: '4px' }}>{profile.education || 'MSc Data Science'}</p>
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Target Roles:</label>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '4px' }}>
                      {profile.target_roles?.map(role => (
                        <span key={role} style={{ fontSize: '10px', background: 'rgba(88, 166, 255, 0.1)', color: 'var(--accent-color)', padding: '2px 8px', borderRadius: '4px', border: '1px solid rgba(88, 166, 255, 0.2)' }}>{role}</span>
                      ))}
                    </div>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', margin: '1rem 0' }}>
                    {profile.skills?.map(skill => (
                      <span key={skill} style={{ fontSize: '10px', background: '#30363d', padding: '2px 8px', borderRadius: '4px', border: '1px solid #444' }}>{skill}</span>
                    ))}
                  </div>
                  <button onClick={() => setIsEditing(true)} className="btn-secondary" style={{ width: '100%', marginBottom: '1rem' }}>Edit Profile</button>
                </>
              ) : (
                <form onSubmit={handleProfileUpdate}>
                  <div style={{ marginBottom: '10px' }}>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Education</label>
                    <input
                      className="form-input"
                      value={profile.education || ''}
                      onChange={(e) => setProfile({ ...profile, education: e.target.value })}
                    />
                  </div>
                  <div style={{ marginBottom: '10px' }}>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Target Roles (comma separated)</label>
                    <input
                      className="form-input"
                      value={profile.target_roles?.join(', ') || ''}
                      onChange={(e) => setProfile({ ...profile, target_roles: e.target.value.split(',').map(s => s.trim()) })}
                    />
                  </div>
                  <div style={{ marginBottom: '10px' }}>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Skills (comma separated)</label>
                    <textarea
                      className="form-input"
                      value={profile.skills?.join(', ') || ''}
                      onChange={(e) => setProfile({ ...profile, skills: e.target.value.split(',').map(s => s.trim()) })}
                      rows={4}
                    />
                  </div>
                  <div style={{ marginBottom: '10px' }}>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Target Email</label>
                    <input
                      className="form-input"
                      value={profile.email || ''}
                      onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    />
                  </div>
                  <div style={{ marginBottom: '10px' }}>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Scan Frequency</label>
                    <select
                      className="form-input"
                      value={profile.scan_frequency || 'daily'}
                      onChange={(e) => setProfile({ ...profile, scan_frequency: e.target.value })}
                    >
                      <option value="6h">Every 6 Hours</option>
                      <option value="12h">Every 12 Hours</option>
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                    </select>
                  </div>
                  <div style={{ marginBottom: '10px' }}>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Telegram Bot Token</label>
                    <input
                      className="form-input"
                      value={profile.telegram_token || ''}
                      onChange={(e) => setProfile({ ...profile, telegram_token: e.target.value })}
                      placeholder="e.g. 123456789:ABCDEF..."
                    />
                  </div>
                  <div style={{ marginBottom: '10px' }}>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Telegram Chat ID</label>
                    <input
                      className="form-input"
                      value={profile.telegram_chat_id || ''}
                      onChange={(e) => setProfile({ ...profile, telegram_chat_id: e.target.value })}
                      placeholder="e.g. 987654321"
                    />
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button type="submit" className="btn-primary" style={{ flex: 1 }}>Save</button>
                    <button type="button" onClick={() => setIsEditing(false)} className="btn-secondary" style={{ flex: 1 }}>Cancel</button>
                  </div>
                </form>
              )}

              <div style={{ marginTop: '1.5rem', background: 'rgba(56, 139, 253, 0.1)', padding: '1rem', borderRadius: '8px', border: '1px solid rgba(56, 139, 253, 0.4)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--accent-color)' }}>PROACTIVE SEARCH</span>
                  <Mail size={14} color="var(--accent-color)" />
                </div>
                <p style={{ fontSize: '11px', margin: '8px 0', color: 'var(--text-secondary)' }}>
                  Agent scans {(profile?.scan_frequency || 'daily').toUpperCase()} and notifies **{profile?.email || 'your email'}**.
                </p>
                <button
                  onClick={triggerScan}
                  style={{ width: '100%', padding: '6px', fontSize: '11px', background: 'var(--accent-color)', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                  Run Discovery Now
                </button>
              </div>

              <hr style={{ border: '0', borderTop: '1px solid var(--border-color)', margin: '1.5rem 0' }} />

              <div style={{ marginTop: '1rem' }}>
                <label className="resume-upload-label">
                  <input type="file" style={{ display: 'none' }} onChange={handleResumeUpload} accept=".pdf" />
                  {uploading ? 'Parsing Resume...' : 'Upload Resume (PDF)'}
                </label>
                <p style={{ fontSize: '10px', color: 'var(--text-secondary)', marginTop: '8px', textAlign: 'center' }}>Auto-extract skills & education</p>
              </div>
            </div>

            <div className="glass-panel" style={{ padding: '1.5rem' }}>
              <h3><BarChart3 size={20} style={{ verticalAlign: 'middle', marginRight: '8px' }} /> Discovery Stats</h3>
              <div style={{ marginTop: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>Daily Scans:</span>
                  <span style={{ color: 'var(--accent-color)', fontWeight: 'bold' }}>Active</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span>Total Found:</span>
                  <span style={{ color: 'var(--accent-color)', fontWeight: 'bold' }}>{data?.total_found || 0}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>Urgent:</span>
                  <span style={{ color: 'var(--warning)', fontWeight: 'bold' }}>{data?.urgent_deadlines.length || 0}</span>
                </div>
              </div>
              <button
                onClick={() => discoverJobs(profile?.target_roles?.join(', '))}
                className="btn-primary"
                style={{ width: '100%', marginTop: '1.5rem', background: 'linear-gradient(45deg, #238636, #2ea043)' }}
                disabled={loading}
              >
                {loading ? 'Discovering...' : 'Scan for Opportunities'}
              </button>
            </div>
          </aside>

          {/* Main Content / Jobs */}
          <section>
            <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1rem', display: 'flex', gap: '10px', alignItems: 'center' }}>
              <div style={{ position: 'relative', flex: 1 }}>
                <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                <input
                  className="form-input"
                  placeholder="Enter keywords (e.g. Frontend, Marketing, AI...)"
                  style={{ paddingLeft: '40px', marginBottom: 0 }}
                  value={searchKeywords}
                  onChange={(e) => setSearchKeywords(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && discoverJobs(searchKeywords)}
                />
              </div>
              <button
                onClick={() => discoverJobs(searchKeywords)}
                className="btn-primary"
                style={{ padding: '0.8rem 1.5rem', marginTop: 0 }}
                disabled={loading}
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>

            {error && (
              <div style={{ padding: '1rem', background: 'rgba(218, 54, 51, 0.1)', border: '1px solid var(--danger)', borderRadius: '8px', marginBottom: '1rem', color: '#ff7b72' }}>
                {error}
              </div>
            )}

            <AnimatePresence>
              {loading ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  style={{ textAlign: 'center', padding: '4rem' }}
                >
                  <div className="spinner"></div>
                  <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>Agent is scouring the web for AI opportunities...</p>
                </motion.div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {data?.internships.map((job, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      className="glass-panel"
                      style={{ padding: '1.5rem', position: 'relative' }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div>
                          <h2 style={{ fontSize: '1.25rem', marginBottom: '4px' }}>{job.role_title}</h2>
                          <p style={{ color: 'var(--accent-color)', fontWeight: '600', marginBottom: '12px' }}>{job.company_name}</p>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <span className={`badge ${job.match_score >= 90 ? 'badge-high' : job.match_score >= 75 ? 'badge-medium' : 'badge-low'}`}>
                            {job.match_score}% Match
                          </span>
                        </div>
                      </div>

                      <div style={{ display: 'flex', gap: '20px', fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><MapPin size={14} /> {job.location}</span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Clock size={14} /> {job.duration || 'N/A'}</span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Calendar size={14} /> DL: {job.application_deadline}</span>
                      </div>

                      <p style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
                        <Zap size={14} style={{ color: 'var(--warning)', marginRight: '4px' }} />
                        <span style={{ color: 'var(--text-primary)' }}>Why it fits:</span> {job.match_reasoning}
                      </p>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', gap: '6px' }}>
                          {job.required_skills.slice(0, 4).map(s => (
                            <span key={s} style={{ fontSize: '11px', color: 'var(--text-secondary)', border: '1px solid var(--border-color)', padding: '2px 8px', borderRadius: '12px' }}>{s}</span>
                          ))}
                        </div>
                        <button
                          className="btn-primary"
                          style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}
                          onClick={() => handleApply(job)}
                        >
                          Apply <ExternalLink size={14} style={{ marginLeft: '4px' }} />
                        </button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </AnimatePresence>
          </section>

        </div>
      </main>

      <style jsx>{`
        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid rgba(88, 166, 255, 0.1);
          border-left-color: var(--accent-color);
          border-radius: 50%;
          display: inline-block;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default App;
