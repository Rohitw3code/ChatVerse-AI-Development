
interface JobItemProps {
  job: {
    id: string;
    title: string;
    organization: string;
    location: string | null;
    url: string;
    date_posted: string;
  };
}

const JobItem = ({ job }: JobItemProps) => {
  return (
    <div className="w-full bg-[#0c0c0c] border border-slate-700 rounded-lg p-4 text-white overflow-hidden">
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-base font-semibold text-white break-words">{job.title}</h3>
      </div>
      {job.organization && <div className="text-sm text-slate-300 mt-1 break-words">{job.organization}</div>}
      {job.location && <p className="text-xs text-slate-400 mt-1 break-words">{job.location}</p>}
      <div className="mt-3 flex items-center gap-4 flex-wrap text-xs text-slate-400">
        <a href={job.url} className="text-violet-400 hover:text-violet-300 underline break-all" target="_blank" rel="noopener noreferrer">
          View on LinkedIn
        </a>
        <span className="text-slate-500">Posted: {job.date_posted}</span>
      </div>
    </div>
  );
};

interface JobOutputFormatterProps {
  toolOutput: {
    type: 'job';
    output: {
      jobs: {
        id: string;
        title: string;
        organization: string;
        location: string | null;
        url: string;
        date_posted: string;
      }[];
    };
  };
}

export function JobOutputFormatter({ toolOutput }: JobOutputFormatterProps) {
  const { jobs } = toolOutput.output;

  if (!jobs || jobs.length === 0) {
    return <div className="text-sm text-slate-400">No job listings found.</div>;
  }

  return (
    <div className="w-full flex flex-col gap-3">
      {jobs.map((job) => (
        <JobItem key={job.id} job={job} />
      ))}
    </div>
  );
}