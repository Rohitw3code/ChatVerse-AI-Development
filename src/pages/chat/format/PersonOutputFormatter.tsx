
// Define the interfaces for the person data
interface PersonProfile {
  id: string;
  full_name: string;
  headline?: string;
  organization?: string;
  location?: string;
  url?: string;
  image_url?: string;
  experience?: string[];
  education?: string[];
  skills?: string[];
}

interface PersonList {
  people: PersonProfile[];
}

interface ToolOutput {
  output: PersonList;
  type: 'person';
}

interface PersonOutputFormatterProps {
  toolOutput: ToolOutput;
}

export function PersonOutputFormatter({ toolOutput }: PersonOutputFormatterProps) {
  const { people } = toolOutput.output;

  if (!people || people.length === 0) {
    return <div className="text-sm text-slate-400">No person profiles found.</div>;
  }

  return (
    <div className="w-full flex flex-col gap-3">
      {people.map((person) => (
        <div key={person.id} className="w-full bg-[#0c0c0c] border border-slate-700 rounded-lg p-4 text-white overflow-hidden">
          <div className="flex items-start gap-3">
            {person.image_url && (
              <img src={person.image_url} alt={person.full_name} className="w-12 h-12 rounded-md object-cover flex-shrink-0" />
            )}
            <div className="min-w-0 flex-1">
              <h3 className="text-base font-semibold text-white break-words">{person.full_name}</h3>
              {person.headline && <p className="text-sm text-slate-300 mt-0.5 break-words">{person.headline}</p>}
              {person.organization && <p className="text-xs text-slate-400 mt-1 break-words"><span className="text-slate-500">Organization:</span> {person.organization}</p>}
              {person.location && <p className="text-xs text-slate-400 mt-0.5 break-words"><span className="text-slate-500">Location:</span> {person.location}</p>}
            </div>
          </div>
          {person.url && (
            <div className="mt-3">
              <a href={person.url} className="text-violet-400 hover:text-violet-300 underline break-all text-xs" target="_blank" rel="noopener noreferrer">View Profile</a>
            </div>
          )}
          {person.experience && person.experience.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-slate-200">Experience</h4>
              <ul className="mt-1 space-y-1 text-sm text-slate-300">
                {person.experience.map((exp, index) => <li key={index} className="break-words">{exp}</li>)}
              </ul>
            </div>
          )}
          {person.education && person.education.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-slate-200">Education</h4>
              <ul className="mt-1 space-y-1 text-sm text-slate-300">
                {person.education.map((edu, index) => <li key={index} className="break-words">{edu}</li>)}
              </ul>
            </div>
          )}
          {person.skills && person.skills.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-slate-200">Skills</h4>
              <ul className="mt-1 flex flex-wrap gap-2">
                {person.skills.map((skill, index) => <li key={index} className="bg-violet-500/10 text-violet-300 border border-violet-600/30 rounded-full px-2 py-0.5 text-xs">{skill}</li>)}
              </ul>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}