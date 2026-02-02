import React from "react";
import type {Task} from "../utility/types";

interface JobsListProps {
    jobs: Task[];   // jobs = tasks, tomato toe-mah-toe.
    setJobById: React.Dispatch<React.SetStateAction<Task | null>>;
    setHideJobDisplay: React.Dispatch<React.SetStateAction<boolean>>;
    selectedId: string | null;
    setSelectedId: React.Dispatch<React.SetStateAction<string | null>>;
}

const JobsList: React.FC<JobsListProps> = ({jobs, setJobById, setHideJobDisplay, selectedId, setSelectedId}) => {

    return(
        <div style={{display:"flex", alignItems:"center", justifyContent:"center"}}>
            <ul id="jobsList" style={{border:"2px solid black", width:"80%", maxHeight:"300px", overflowY:"scroll", paddingLeft:"10px", paddingRight:"10px"}}>
                {jobs.map((job) => {
                    const isSelected = job.id === selectedId;

                    return(
                        <li
                            key={job.id}
                            style={{border:"2px solid black", marginTop:"10px", marginBottom:"10px", cursor:"pointer", backgroundColor: isSelected ? "#cceeff" : "white"}}
                            onClick={()=>{setJobById(job); setSelectedId(job.id); setHideJobDisplay(true);}}   // Clicking on a specific Job in the list will open the "specific Job display box".
                        >
                            {/*In the Jobs List, I'm just going to have ID and status (for more information, you need to expand info):*/}
                            <div><b>ID:</b>{job.id}</div>
                            <div><b>Status:</b>{job.status}</div>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};

export default JobsList;