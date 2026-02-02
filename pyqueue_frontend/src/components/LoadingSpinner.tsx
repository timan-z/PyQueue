import React, { type SetStateAction } from "react";
import {deleteJob, retryJob} from "../utility/api";
import type {Task} from "../utility/types";

interface JobDisplayProps {
    job: Task | null;
    refreshJobs: () => void;
    setLoading: React.Dispatch<SetStateAction<boolean>>;
    setJobById: React.Dispatch<SetStateAction<Task | null>>;
}

const JobDisplay: React.FC<JobDisplayProps> = ({job, refreshJobs, setLoading, setJobById}) => {

    const goDeleteJob = async(id: string) => {
        // TO-DO:(?) Insert setLoading (port that state function here?)
        setLoading(true)
        try {
            await deleteJob(id);
        } catch(err: any) {
            console.error("[goDeleteJob]ERROR: SOMETHING BAD HAPPEN!!!");
            console.log("Something bad happened... what could it be!");
        } finally {
            setJobById(null);
            refreshJobs();
            setLoading(false);
        }
    }

    const goRetryJob = async(id: string) => {
        setLoading(true);
        try {
            await retryJob(id)
        } catch(err: any) {
            console.error("[goRetryJob]ERROR: SOMETHING BAD HAPPEN!!!");
            console.log("Something bad happened... what could it be!");
        } finally {
            setLoading(false);
            try {
                refreshJobs();
                //setJobById(null); // <-- not necessary here I don't think
            } catch(err: any) {
                console.error("[goRetryJob]ERROR: There was an issue with refreshing the list of jobs.");
            } finally {
                console.log("Refreshed list of jobs post-retry attempt.");
            }
        }
    }

    return(
        <div id="jobDisplayBox">
            <div id="jobDisplayBoxInfo">
                <div><b>ID:</b>{job?.id}</div>
                <div><b>Status:</b>{job?.status}</div>
                <div><b>Payload:</b>{job?.payload}</div>
                <div><b>Type:</b>{job?.type}</div>
                <div><b>Attempts:</b>{job?.attempts}</div>
                <div><b>Max Retries:</b>{job?.maxRetries}</div>
                <div><b>Created At:</b>{job?.createdAt}</div>
            </div>
            
            {/* Buttons to interact w/ the Job Display Box. (Delete specific job or Retry if it failed): */}
            <div id="jobDisplayBoxBtns">
                {/* Want a button here that lets you delete this Job: */}
                <button onClick={()=>goDeleteJob(job!.id)}>Delete this Job</button>
                
                {/* Want a button here that lets you retry this Job if it failed: */}
                {job?.status == "failed" && <button onClick={()=>goRetryJob(job!.id)}>Retry this Job</button>}
            </div>
        </div>
    );
};

export default JobDisplay;