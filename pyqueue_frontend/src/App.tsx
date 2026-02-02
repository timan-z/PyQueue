import { useEffect, useState } from 'react'
import './App.css'
import {getAllJobs, getJobById, enqueueJob, clearQueue} from './utility/api'
import type {Task} from './utility/types'
import JobsList from './components/JobsList'
import JobDisplay from './components/JobDisplay'
import LoadingSpinner from './components/LoadingSpinner'

function App() {
  const [loading, setLoading] = useState(false);
  const [allJobs, setAllJobs] = useState <Task[]>([]);
  const [getJobId, setGetJobId] = useState <string>("");
  const [jobById, setJobById] = useState <Task | null>(null);
  const [hideJobsList, setHideJobsList] = useState(false);
  const [hideJobDisplay, setHideJobDisplay] = useState(false);
  const [enqueueJobPL, setEnqueueJobPL] = useState<string>("");
  const [enqueueJobType, setEnqueueJobType] = useState<string>("--");
  const [enqJobPLEmpty, setEnqJobPLEmpty] = useState(false);
  const [enqJobTypeEmpty, setEnqJobTypeEmpty] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  /* Cosmetic useEffect hook for tweaking the display text of the Toggle Jobs List button: */
  useEffect(() => {
    const toggleText = document.getElementById("hideJobsList");
    if(hideJobsList) {
      toggleText!.textContent = "Hide Jobs List"
    } else {
      toggleText!.textContent = "Show Jobs List"
    }
  }, [hideJobsList]);
  /* Another one ^ but for the Toggle Individual Job Display button: */
  useEffect(() => {
    const toggleText = document.getElementById("toggleJobDispl");
    if(hideJobDisplay) {
      toggleText!.textContent = "Show Job Display"
    } else {
      toggleText!.textContent = "Hide Job Display"
    }
  }, [hideJobDisplay]);

  // function to invoke API fetch function "getAllJobs" ([GET /api/jobs]):
  const goGetAllJobs = async() => {
    setLoading(true);
    try {
      const res = await getAllJobs();
      if(res) {
        setAllJobs(res)
      }
    } catch(err: any) {
      console.error("[goGetAllJobs]ERROR: SOMETHING BAD HAPPEN!!!");
    } finally {
      setLoading(false);
      if(!hideJobsList) {
        setHideJobsList(hideJobsList => !hideJobsList);
      }
    }
  }

  // function to invoke API fetch function "getJobById" ([GET /api/jobs/:id]):
  const goGetJobById = async(event: any) => {
    event.preventDefault();
    setLoading(true);
    try {
      const res = await getJobById(getJobId);
      if(res) {
        setJobById(res)
      }
    } catch(err: any) {
      console.error("[goGetJobById]ERROR: SOMETHING BAD HAPPEN!!!");
    } finally {
      setSelectedId(null);
      setLoading(false);
    }
  }

  // function to invoke API fetch function "enqueueJob" ([POST /api/enqueue]):
  const goEnqueueJob = async(event: any) => {
    event.preventDefault();
    if(enqueueJobPL.trim() == "") {
      setEnqJobPLEmpty(true);
      setTimeout(() => setEnqJobPLEmpty(false), 2500);
      return;
    }
    if(enqueueJobType == "--") {
      setEnqJobTypeEmpty(true);
      setTimeout(() => setEnqJobTypeEmpty(false), 2500);
      return;
    }

    setLoading(true);
    try {
      await enqueueJob(enqueueJobPL, enqueueJobType);
    } catch(err: any) {
      console.error("[goEnqueueJob]ERROR: SOMETHING BAD HAPPEN!!! => ", err);
    } finally {
      await goGetAllJobs();
      setLoading(false);
    }
  }

  // function to invoke API fetch function "clearQueue" ([POST /api/clear]):
  const goClearQueue = async() => {
    setLoading(true);
    try {
      await clearQueue();
    } catch(err: any) {
      console.error("[goClearQueue]ERROR: SOMETHING BAD HAPPEN!!! => ", err);
    } finally {
      await goGetAllJobs();
      setJobById(null);
      setLoading(false);
    }
  }

  return (
    <div id="mainPageWrapper">
      {/* Header: */}
      <header id="pageTitle">
        <h1 id="mainHeader" className="headerEl">PyQueue</h1>
        <h2 className="headerEl">Basically just a bare-essentials simulation of Task Queue programs like Celery and Sidekiq</h2>
        <p id="pageUndertext">The (backend) logic of which was built entirely in <b>Python-FastAPI</b> (to help better understand <b>FastAPI</b>) with a ReactTS-based Dashboard (<i>which is what you're on now</i>).</p>
      </header>

      {/* Main Body: */}
      <main>
        {/* 1. Enqueue Job Area: */}
        <div id="enqueueJobArea">
          <form id="enqJobAreaForm" onSubmit={goEnqueueJob}>
            <div style={{display:"flex", flexDirection:"column"}}>              
              {enqJobPLEmpty && <div style={{color: "#FF4C4C",fontSize: "14px",marginBottom: "5px",animation: "fadeInOut 2.5s ease-in-out",}}>
                ⚠ Don't leave empty!
              </div>}

              <input
                type="text"
                id="enqueueJobPLInput"
                value={enqueueJobPL}
                placeholder="Enter Job Payload"
                style={{fontFamily:"monospace"}}
                onChange={(e) => setEnqueueJobPL(e.target.value)}
              />
            </div>

            {/* Allow user to select type of job/task: */}
            <div style={{display:"flex", flexDirection:"column"}}>
              {enqJobTypeEmpty && <div style={{color: "#FF4C4C",fontSize: "14px",marginBottom: "5px",animation: "fadeInOut 2.5s ease-in-out",}}>
                ⚠ Pick a type!
              </div>}

              <div style={{color:"white"}}>
                <label htmlFor="enqJobTypeSelect">Select Job Type:</label>
                <select id="enqJobTypeSelect" style={{fontFamily:"monospace"}} onChange={(e) => setEnqueueJobType(e.target.value)} value={enqueueJobType}>
                  <option value="--">--</option>
                  <option value="email">email (2s)</option>
                  <option value="report">report (5s)</option>
                  <option value="data-cleanup">data-cleanup (3s)</option>
                  <option value="sms">sms (1s)</option>
                  <option value="newsletter">newsletter (4s)</option>
                  <option value="takes-long">takes-long (10s)</option>
                  <option value="fail">fail (2s)</option>
                  <option value="fail-absolute">fail-absolute (2s)</option>
                </select>
              </div>
            </div>

            <button type="submit">Enqueue Job</button>
          </form>

          {/* Loading Spinner (present for however long each API fetch function lasts): */}
          {loading && <LoadingSpinner/>}
        </div>

        {/* 2. Area where you can "View All Jobs" and "Clear Jobs List" (primarily, among other things): */}      
        <div id="jobsListArea">
          <div id="jobsListAreaBtns">
            <button id="getAllJobsBtn" type="submit" onClick={()=>goGetAllJobs()}>Get All Jobs</button> 
            <button id="hideJobsList" type="submit" onClick={()=>setHideJobsList(hideJobsList => !hideJobsList)}>Hide Jobs List</button>
            <button type="submit" onClick={()=>goClearQueue()}>Clear Jobs List</button>
          </div>
          {/* Jobs List: */}
          {hideJobsList && (<JobsList jobs={allJobs} setJobById={setJobById} setHideJobDisplay={setHideJobDisplay} selectedId={selectedId} setSelectedId={setSelectedId}/>)}
        </div>

        {/* 3. Area where you can view individual jobs in all their specifics: */}
        <div id="indivJobArea">

          <div id="indivJobAreaBtns">
            {/* Form below with text-input for id so we can (call the function that) do(es) the [GET /api/jobs/{id}] request: */}
            <form onSubmit={goGetJobById}>
              <input
                type="text"
                id="getJobByIdInput"
                value={getJobId}
                style={{fontFamily:"monospace"}}
                placeholder="Enter Job ID"
                onChange={(e) => setGetJobId(e.target.value)}
              />
              <button type="submit">Get Specific Job</button>
            </form>
            <button id="toggleJobDispl" type="submit" onClick={()=>setHideJobDisplay(hideJobDisplay => !hideJobDisplay)}>Show Job Display</button>
          </div>

          {/* Have the Specific Job Display "Highlight Area" goes here (nothing too fancy yet): */}
          <div id="jobDisplayBoxWrapper">
            {hideJobDisplay && jobById && (<JobDisplay job={jobById} refreshJobs={goGetAllJobs} setLoading={setLoading} setJobById={setJobById}/>)}
          </div>
        </div>

        {/* Small About Panel: */}
        <div id="AboutPanel">
          <h2>ABOUT PANEL:</h2>

          <div style={{ textAlign:"left" }}>
            <b>PyQueue</b> is the Python/FastAPI evolution of my earlier task-queue projects, following
            <a href="https://goqueue.netlify.app/" target="_blank" rel="noreferrer" style={{ textDecoration:"none"}} > GoQueue</a> (Go)
            and <a href="https://springqueue.netlify.app/" target="_blank" rel="noreferrer" style={{ textDecoration:"none"}} > SpringQueue</a> (Java/Spring Boot),
            and informed by the more production-oriented <b>SpringQueuePro</b>.
            <br /><br />
            While SpringQueuePro represents the most feature-complete and production-heavy implementation,
            PyQueue focuses on translating those architectural ideas into the Python ecosystem using FastAPI.
            It emphasizes explicit dependency management, clear API contracts, backend-first design, and
            deliberate separation between domain models and API schemas.
            <br /><br />
            Rather than being a simple port, PyQueue serves as a comparative backend study—highlighting how
            concurrency, dependency injection, and service boundaries differ between Go, Java/Spring, and
            Python/FastAPI while preserving the same core Producer–Consumer queue model.
          </div>

          <ul>
            <li>Fixed worker pool (3 workers) with an in-memory task registry.</li>
            <li>Task execution times vary by task type to simulate real-world workloads.</li>
            <li>Retry behavior and execution metadata are exposed for inspection and learning.</li>
          </ul>

          Currently hosted on Netlify (frontend) and Railway (backend).
          See the <a href="https://github.com/timan-z/PyQueue" target="_blank" rel="noreferrer" style={{ textDecoration:"none"}}>README and GitHub repo</a> for deeper technical details.
        </div>
      </main>
    </div>
  )
}

export default App
