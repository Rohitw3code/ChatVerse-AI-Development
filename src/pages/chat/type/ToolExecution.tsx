import { useState } from "react";
import { ApiMessage } from "../types";
import { SuccessIcon, LinkedInIcon, GmailIcon, InstagramIcon, YouTubeIcon, TavilyIcon, DocsIcon, SheetsIcon } from "../ui/shared/platforms";
import { ToolOutputFormatter } from "../format/ToolOutputFormatter";
import { EmailDraftOutputFormatter } from "../format/EmailDraftOutputFormatter";
import { JobOutputFormatter } from "../format/JobOutputFormatter";
import { PersonOutputFormatter } from "../format/PersonOutputFormatter"; 

const ChevronIcon = ({ isOpen }: { isOpen: boolean }) => (
    <svg
      className={`w-5 h-5 text-slate-500 transition-transform duration-300 ease-out ${isOpen ? 'rotate-180' : ''}`}
      viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
    >
      <polyline points="6 9 12 15 18 9"></polyline>
    </svg>
);

const PLATFORM_ICONS: { [key: string]: JSX.Element } = {
  gmail: <GmailIcon />,
  instagram: <InstagramIcon />,
  linkedin: <LinkedInIcon />,
  youtube: <YouTubeIcon />,
  tavily: <TavilyIcon />,
  gdoc: <DocsIcon />,
  docs: <DocsIcon />,
  sheets: <SheetsIcon />
};

type NodeWidth = 'full' | '1/2' | '2/3' | '1/3';
type NodeConfig = { platform: string; name: string; width?: NodeWidth };

const NODE_CONFIG: { [key: string]: NodeConfig } = {
  verify_gmail_connection: { platform: 'gmail', name: "Verifying Gmail Access" },
  send_gmail: { platform: 'gmail', name: "Sending Email" },
  draft_gmail: { platform: 'gmail', name: "Drafting Email" ,width:'full'},
  reply_to_email: { platform: 'gmail', name: "Replying to Email" },
  search_gmail: { platform: 'gmail', name: "Searching Email" },
  fetch_recent_gmail: { platform: 'gmail', name: "Fetching Recent Emails" },
  research_agent_node: { platform: 'gmail', name: "Fetching Recent Emails" },
  tavily_search: { platform: 'tavily', name: "Search on internet" },
  fetch_youtube_traffic_sources: { platform: 'youtube', name: "Fetching YouTube Traffic Sources",width:"full" },
  gmail_error: { platform: 'gmail', name: "Something went wrong in Gmail" },
  fetch_unread_gmail: { platform: 'gmail', name: "Fetching Unread Emails" },
  profile_insight: { platform: 'instagram', name: "Fetching Instagram Profile" },
  instagram_auth_verification: { platform: 'instagram', name: "Verifying Instagram Access" },
  get_profile_info: { platform: 'instagram', name: "Getting Profile Information" },
  get_recent_posts: { platform: 'instagram', name: "Fetching Recent Posts" },
  get_top_posts: { platform: 'instagram', name: "Fetching Top Posts" },
  get_post_insights: { platform: 'instagram', name: "Analyzing Post Insights", width: '2/3' },
  get_post_comments: { platform: 'instagram', name: "Fetching Post Comments" },
  search_hashtag: { platform: 'instagram', name: "Searching Hashtag" },
  publish_post: { platform: 'instagram', name: "Publishing Post" },
  instagram_error: { platform: 'instagram', name: "Something went wrong in Instagram" },
  youtube_error: { platform: 'youtube', name: "Something went wrong in YouTube" },
  fetch_youtube_analytics_overview: { platform: 'youtube', name: "Fetching YouTube Analytics Overview" },
  fetch_youtube_channel_videos: { platform: 'youtube', name: "Fetching YouTube Channel Videos" },
  linkedin_job_search: { platform: 'linkedin', name: "Looking for job on LinkedIn",width:'full' },
  linkedin_person_search: { platform: 'linkedin', name: "Searching person on LinkedIn" },
  fetch_youtube_channel_details: {platform:'youtube',name:"Fetching YouTube Channel Details",width:'2/3'},
  // Google Docs tools
  create_gdoc_document: { platform: 'gdoc', name: 'Creating Google Doc', width: '2/3' },
  append_gdoc_text_return_url: { platform: 'gdoc', name: 'Updating Google Doc', width: '2/3' },
  login_gdoc_account: { platform: 'gdoc', name: 'Google Docs Authentication' },
  
  // Google Sheets tools
  verify_sheets_connection: { platform: 'sheets', name: 'Verifying Google Sheets Access' },
  create_spreadsheet: { platform: 'sheets', name: 'Creating Spreadsheet', width: '2/3' },
  read_sheet_data: { platform: 'sheets', name: 'Reading Range', width: '2/3' },
  write_sheet_data: { platform: 'sheets', name: 'Writing Data', width: '2/3' },
  append_sheet_data: { platform: 'sheets', name: 'Appending Data', width: '2/3' },
  clear_sheet_data: { platform: 'sheets', name: 'Clearing Range' },
  list_spreadsheets: { platform: 'sheets', name: 'Listing Spreadsheets', width: '2/3' },
  draft_spreadsheet: { platform: 'sheets', name: 'Drafting Spreadsheet', width: '2/3' },
  login_to_sheets: { platform: 'sheets', name: 'Google Sheets Authentication' },
};

export const TRACKED_TOOL_NODES = new Set(Object.keys(NODE_CONFIG));
const EXPAND_NODE = new Set(['draft_email', 'job','person']);

interface ToolExecutionProps {
  message: ApiMessage;
}

export function ToolExecution({ message }: ToolExecutionProps) {
  const [isOpen, setIsOpen] = useState(EXPAND_NODE.has(message.tool_output?.type));

  const config = NODE_CONFIG[message.node];
  const isExecuting = message.status !== 'success' && message.status !== 'failed';
  const isSuccess = message.status === 'success';
  const isFinished = !isExecuting;

  if (!config) return null;

  const platformIcon = PLATFORM_ICONS[config.platform];
  const WIDTH_CLASS_MAP: Record<NodeWidth, string> = {
    full: 'md:w-full',
    '1/2': 'md:w-1/2',
    '2/3': 'md:w-2/3',
    '1/3': 'md:w-1/3',
  };
  const widthClass = WIDTH_CLASS_MAP[config.width ?? '1/2'];

  const containerClasses = [
    // Full width on small screens; apply configured width from md+
    // Reduced padding on mobile for more space
    `relative flex flex-col gap-2 p-2 sm:p-2.5 md:p-3 rounded-xl w-full ${widthClass} bg-zinc-800 border border-slate-700 shadow-inner transition-colors duration-200 overflow-hidden`,
    isFinished ? "cursor-pointer hover:bg-zinc-700" : "",
    isSuccess ? "border-green-500/50" : ""
  ].join(" ");

  const statusClasses = [
    "text-xs text-slate-500 mt-1 font-medium transition-colors duration-300",
    isSuccess ? "text-green-500" : ""
  ].join(" ");



  return (
    <div className={containerClasses}>
      <div className="flex gap-2 sm:gap-2.5 md:gap-3 items-center w-full min-w-0" onClick={() => isFinished && setIsOpen(!isOpen)}>
        <div className="flex-shrink-0 p-1.5 sm:p-2 bg-violet-500/10 rounded-lg">{platformIcon}</div>
        <div className="flex-grow min-w-0">
          <div className="flex items-center justify-between font-semibold text-white">
            <div className="flex items-center gap-2 min-w-0">
              <span className="break-words text-sm sm:text-base">{config.name}</span>
            </div>
            {isExecuting && <div className="w-4 h-4 border-2 border-violet-500/30 border-t-violet-500 rounded-full animate-spin"></div>}
            {isSuccess && <SuccessIcon />}
          </div>
          <div className={statusClasses}>
            Status: {isExecuting ? 'in progress...' : message.status}
          </div>
        </div>
        {isFinished && <ChevronIcon isOpen={isOpen} />}
      </div>

      {isOpen && isFinished && message.tool_output && (
        <div className="bg-transparent rounded-lg mt-2.5 w-full">
          {message.tool_output.type === 'draft_email' ? (
            <EmailDraftOutputFormatter toolOutput={message.tool_output as any} />
          ) : message.tool_output.type === 'job' ? (
            <JobOutputFormatter toolOutput={message.tool_output as any} />
          ) : message.tool_output.type === 'person' ? (
            <PersonOutputFormatter toolOutput={message.tool_output as any} />
          ) : (
            <ToolOutputFormatter toolOutput={message.tool_output as any} />
          )}
        </div>
      )}
    </div>
  );
}