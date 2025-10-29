import React, { useState } from "react";
import { ApiMessage } from "../../types";
import { SuccessIcon, LinkedInIcon, GmailIcon, InstagramIcon,YouTubeIcon } from "./platforms";

const ChevronIcon = ({ isOpen }: { isOpen: boolean }) => (
  <svg 
    className={`dropdown-chevron ${isOpen ? 'open' : ''}`} 
    width="20" height="20" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
  >
    <polyline points="6 9 12 15 18 9"></polyline>
  </svg>
);

const PLATFORM_ICONS: { [key: string]: JSX.Element } = {
  gmail: <GmailIcon />,
  instagram: <InstagramIcon />,
  linkedin: <LinkedInIcon />,
  youtube: <YouTubeIcon/>
};

const NODE_CONFIG: { [key: string]: { platform: string; name: string } } = {
  send_email: { platform: 'gmail', name: "Sending Email" },
  write_email: { platform: 'gmail', name: "Drafting Email" },
  get_unread_email:{platform:'gmail',name:"Unread Gmails"},
  tavily_search:{platform:'gmail',name:"Searching Tavily"},
  profile_insight: { platform: 'instagram', name: "Fetching Instagram Profile" },
  instagram_auth_verification: { platform: 'instagram', name: "Verifying Instagram Access" },
  get_profile_info: { platform: 'instagram', name: "Getting Profile Information" },
  get_recent_posts: { platform: 'instagram', name: "Fetching Recent Posts" },
  get_top_posts: { platform: 'instagram', name: "Fetching Top Posts" },
  get_post_insights: { platform: 'instagram', name: "Analyzing Post Insights" },
  get_post_comments: { platform: 'instagram', name: "Fetching Post Comments" },
  search_hashtag: { platform: 'instagram', name: "Searching Hashtag" },
  publish_post: { platform: 'instagram', name: "Publishing Post" },
  ask_human: { platform: 'instagram', name: "Requesting User Input" },
  instagram_error: { platform: 'instagram', name: "Something went wrong in Instagram" },
  linkedin_job_search: { platform: 'linkedin', name: "Looking for job on LinkedIn" },
  fetch_youtube_channel_details: {platform:'youtube',name:"Fetching YouTube Channel Details"},
};

export const TRACKED_TOOL_NODES = new Set(Object.keys(NODE_CONFIG));

interface ToolExecutionProps {
  message: ApiMessage;
}

export function ToolExecution({ message }: ToolExecutionProps) {
  const [isOpen, setIsOpen] = useState(false);
  const config = NODE_CONFIG[message.node];
  // alert("config : "+JSON.stringify(config))
  const isExecuting = message.status !== 'success' && message.status !== 'failed';
  const isSuccess = message.status === 'success';
  const isFinished = !isExecuting;

  if (!config) return null;

  const platformIcon = PLATFORM_ICONS[config.platform];

  return (
    <div
      className={`tool-execution-container ${isSuccess ? 'success' : ''} ${isFinished ? 'is-finished' : ''}`}
      onClick={isFinished ? () => setIsOpen(!isOpen) : undefined}
    >
      <div className="tool-main-content">
        <div className="tool-icon">{platformIcon}</div>
        <div className="tool-content">
          <div className="tool-header">
            <div className="tool-header-info">
              <span>{config.name}</span>
            </div>
            {isExecuting && <div className="spinner"></div>}
            {isSuccess && <SuccessIcon />}
          </div>
          <div className="tool-status">
            Status: {isExecuting ? 'in progress...' : message.status}
          </div>
        </div>
        {isFinished && <ChevronIcon isOpen={isOpen} />}
      </div>

      {isOpen && isFinished && (
        <div className="tool-output-dropdown">
          <pre className="tool-output-pre">{JSON.stringify(message.tool_output, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}