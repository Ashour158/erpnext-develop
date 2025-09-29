import React, { useState, useEffect, useCallback } from 'react';
import {
  DocumentTextIcon,
  TableCellsIcon,
  CalendarIcon,
  ChatBubbleLeftRightIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  MagnifyingGlassIcon,
  PlusIcon,
  StarIcon,
  TagIcon,
  ClockIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon,
  ShareIcon,
  HeartIcon,
  BookmarkIcon,
  ArrowPathIcon,
  SparklesIcon,
  CommandLineIcon,
  LightBulbIcon,
  ChartBarIcon,
  DocumentDuplicateIcon,
  FolderIcon,
  LinkIcon,
  PhotoIcon,
  VideoCameraIcon,
  MicrophoneIcon,
  CodeBracketIcon,
  ListBulletIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  QuestionMarkCircleIcon,
  LightBulbIcon as BulbIcon,
  RocketLaunchIcon,
  CpuChipIcon,
  CloudIcon,
  ShieldCheckIcon,
  LockClosedIcon,
  KeyIcon,
  UserIcon,
  UsersIcon,
  BuildingOfficeIcon,
  GlobeAltIcon,
  DevicePhoneMobileIcon,
  ComputerDesktopIcon,
  TabletIcon,
  WatchIcon,
  HeadphonesIcon,
  SpeakerWaveIcon,
  VolumeXIcon,
  VolumeUpIcon,
  PlayIcon,
  PauseIcon,
  StopIcon,
  ForwardIcon,
  BackwardIcon,
  SkipForwardIcon,
  SkipBackwardIcon,
  ShuffleIcon,
  ArrowPathIcon as RepeatIcon,
  ArrowUturnLeftIcon,
  ArrowUturnRightIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ChevronDoubleUpIcon,
  ChevronDoubleDownIcon,
  ChevronDoubleLeftIcon,
  ChevronDoubleRightIcon,
  MinusIcon,
  XMarkIcon,
  CheckIcon,
  ExclamationTriangleIcon as WarningIcon,
  InformationCircleIcon as InfoIcon,
  QuestionMarkCircleIcon as QuestionIcon,
  LightBulbIcon as IdeaIcon,
  SparklesIcon as MagicIcon,
  CommandLineIcon as TerminalIcon,
  CodeBracketIcon as CodeIcon,
  DocumentTextIcon as DocumentIcon,
  TableCellsIcon as TableIcon,
  CalendarIcon as CalendarIconComponent,
  ChatBubbleLeftRightIcon as ChatIcon,
  UserGroupIcon as GroupIcon,
  Cog6ToothIcon as SettingsIcon,
  MagnifyingGlassIcon as SearchIcon,
  PlusIcon as AddIcon,
  StarIcon as StarIconComponent,
  TagIcon as TagIconComponent,
  ClockIcon as TimeIcon,
  EyeIcon as ViewIcon,
  PencilIcon as EditIcon,
  TrashIcon as DeleteIcon,
  ShareIcon as ShareIconComponent,
  HeartIcon as HeartIconComponent,
  BookmarkIcon as BookmarkIconComponent,
  ArrowPathIcon as RefreshIcon,
  SparklesIcon as SparkleIcon,
  CommandLineIcon as CommandIcon,
  LightBulbIcon as LightBulbIconComponent,
  ChartBarIcon as ChartIcon,
  DocumentDuplicateIcon as CopyIcon,
  FolderIcon as FolderIconComponent,
  LinkIcon as LinkIconComponent,
  PhotoIcon as ImageIcon,
  VideoCameraIcon as VideoIcon,
  MicrophoneIcon as AudioIcon,
  CodeBracketIcon as CodeBracketIconComponent,
  ListBulletIcon as ListIcon,
  CheckCircleIcon as CheckIconComponent,
  XCircleIcon as XIcon,
  ExclamationTriangleIcon as ExclamationIcon,
  InformationCircleIcon as InfoCircleIcon,
  QuestionMarkCircleIcon as QuestionCircleIcon
} from '@heroicons/react/24/outline';

// Types
interface Workspace {
  id: string;
  name: string;
  description: string;
  type: 'personal' | 'team' | 'organization' | 'public';
  members: string[];
  admins: string[];
  isPublic: boolean;
  icon?: string;
  coverImage?: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

interface Page {
  id: string;
  title: string;
  content: any[];
  type: 'page' | 'database' | 'template' | 'wiki' | 'document' | 'presentation' | 'spreadsheet';
  workspaceId: string;
  parentId?: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  lastEditedBy: string;
  isPublished: boolean;
  isArchived: boolean;
  permissions: Record<string, string>;
  properties: Record<string, any>;
  tags: string[];
  icon?: string;
  coverImage?: string;
}

interface Database {
  id: string;
  title: string;
  description: string;
  workspaceId: string;
  pageId: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  properties: Record<string, any>;
  views: any[];
  records: any[];
  isPublic: boolean;
  permissions: Record<string, string>;
  settings: Record<string, any>;
}

interface Template {
  id: string;
  name: string;
  description: string;
  type: 'page' | 'database' | 'workflow' | 'automation' | 'form' | 'presentation' | 'document' | 'spreadsheet';
  content: Record<string, any>;
  variables: string[];
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  usageCount: number;
  isPublic: boolean;
  isFeatured: boolean;
  tags: string[];
  category: string;
  icon?: string;
  coverImage?: string;
  permissions: Record<string, string>;
}

interface AIAssistant {
  isActive: boolean;
  conversations: any[];
  templates: any[];
  analytics: Record<string, any>;
}

interface CollaborativeEditing {
  activeSessions: number;
  totalOperations: number;
  activeCursors: number;
  totalConflicts: number;
  unresolvedConflicts: number;
  operationsByType: Record<string, number>;
  averageSessionDuration: number;
  conflictResolutionRate: number;
}

interface DatabaseSystem {
  totalDatabases: number;
  totalRecords: number;
  totalProperties: number;
  totalViews: number;
  publicDatabases: number;
  databasesByType: Record<string, number>;
  propertiesByType: Record<string, number>;
}

interface TemplateSystem {
  totalTemplates: number;
  publicTemplates: number;
  featuredTemplates: number;
  totalAutomations: number;
  activeAutomations: number;
  totalUsage: number;
  templatesByType: Record<string, number>;
  templatesByCategory: Record<string, number>;
  mostUsedTemplates: any[];
}

interface NotionLikeDashboardProps {
  className?: string;
}

const NotionLikeDashboard: React.FC<NotionLikeDashboardProps> = ({ className = '' }) => {
  // State
  const [activeTab, setActiveTab] = useState<'workspace' | 'pages' | 'databases' | 'templates' | 'ai' | 'collaboration' | 'analytics'>('workspace');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedWorkspace, setSelectedWorkspace] = useState<string>('');
  const [selectedPage, setSelectedPage] = useState<string>('');
  const [selectedDatabase, setSelectedDatabase] = useState<string>('');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createType, setCreateType] = useState<'page' | 'database' | 'template' | 'workspace'>('page');
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  const [aiQuery, setAiQuery] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [isAiProcessing, setIsAiProcessing] = useState(false);

  // Mock data
  const [workspaces] = useState<Workspace[]>([
    {
      id: '1',
      name: 'Personal Workspace',
      description: 'Your personal workspace',
      type: 'personal',
      members: ['user1'],
      admins: ['user1'],
      isPublic: false,
      tags: ['personal'],
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z'
    },
    {
      id: '2',
      name: 'Team Workspace',
      description: 'Team collaboration workspace',
      type: 'team',
      members: ['user1', 'user2', 'user3'],
      admins: ['user1'],
      isPublic: false,
      tags: ['team', 'collaboration'],
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z'
    }
  ]);

  const [pages] = useState<Page[]>([
    {
      id: '1',
      title: 'Welcome to Notion-like Dashboard',
      content: [],
      type: 'page',
      workspaceId: '1',
      createdBy: 'user1',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      lastEditedBy: 'user1',
      isPublished: true,
      isArchived: false,
      permissions: {},
      properties: {},
      tags: ['welcome', 'getting-started']
    },
    {
      id: '2',
      title: 'Project Planning',
      content: [],
      type: 'page',
      workspaceId: '1',
      createdBy: 'user1',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      lastEditedBy: 'user1',
      isPublished: true,
      isArchived: false,
      permissions: {},
      properties: {},
      tags: ['project', 'planning']
    }
  ]);

  const [databases] = useState<Database[]>([
    {
      id: '1',
      title: 'Task Database',
      description: 'Manage tasks and assignments',
      workspaceId: '1',
      pageId: '1',
      createdBy: 'user1',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      properties: {},
      views: [],
      records: [],
      isPublic: false,
      permissions: {},
      settings: {}
    }
  ]);

  const [templates] = useState<Template[]>([
    {
      id: '1',
      name: 'Meeting Notes',
      description: 'Template for meeting notes and minutes',
      type: 'page',
      content: {},
      variables: ['meeting_title', 'date', 'time', 'attendees'],
      createdBy: 'system',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 150,
      isPublic: true,
      isFeatured: true,
      tags: ['meeting', 'notes', 'minutes'],
      category: 'meeting',
      permissions: {}
    },
    {
      id: '2',
      name: 'Project Plan',
      description: 'Template for project planning and management',
      type: 'page',
      content: {},
      variables: ['project_name', 'project_manager', 'start_date', 'end_date'],
      createdBy: 'system',
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-01-01T00:00:00Z',
      usageCount: 200,
      isPublic: true,
      isFeatured: true,
      tags: ['project', 'planning', 'management'],
      category: 'project',
      permissions: {}
    }
  ]);

  const [aiAssistant] = useState<AIAssistant>({
    isActive: true,
    conversations: [],
    templates: [],
    analytics: {
      totalConversations: 0,
      activeConversations: 0,
      totalTemplates: 0,
      publicTemplates: 0,
      totalRequests: 0,
      averageConfidence: 0.0,
      mostUsedTemplates: []
    }
  });

  const [collaborativeEditing] = useState<CollaborativeEditing>({
    activeSessions: 5,
    totalOperations: 1250,
    activeCursors: 12,
    totalConflicts: 8,
    unresolvedConflicts: 2,
    operationsByType: {
      insert: 500,
      delete: 300,
      retain: 400,
      format: 50
    },
    averageSessionDuration: 45.5,
    conflictResolutionRate: 0.75
  });

  const [databaseSystem] = useState<DatabaseSystem>({
    totalDatabases: 15,
    totalRecords: 2500,
    totalProperties: 150,
    totalViews: 45,
    publicDatabases: 5,
    databasesByType: {
      table: 10,
      board: 3,
      timeline: 1,
      calendar: 1
    },
    propertiesByType: {
      title: 15,
      text: 50,
      number: 30,
      select: 25,
      date: 20,
      checkbox: 10
    }
  });

  const [templateSystem] = useState<TemplateSystem>({
    totalTemplates: 50,
    publicTemplates: 35,
    featuredTemplates: 10,
    totalAutomations: 25,
    activeAutomations: 20,
    totalUsage: 5000,
    templatesByType: {
      page: 30,
      database: 15,
      workflow: 3,
      automation: 2
    },
    templatesByCategory: {
      meeting: 10,
      project: 8,
      productivity: 12,
      crm: 5,
      other: 15
    },
    mostUsedTemplates: []
  });

  // Handlers
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    // Implement search logic
  }, []);

  const handleCreateItem = useCallback((type: 'page' | 'database' | 'template' | 'workspace') => {
    setCreateType(type);
    setShowCreateModal(true);
  }, []);

  const handleAIAssistant = useCallback(async (query: string) => {
    setIsAiProcessing(true);
    setAiQuery(query);
    
    try {
      // Simulate AI processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      setAiResponse(`AI Response: ${query}`);
    } catch (error) {
      console.error('AI Assistant error:', error);
    } finally {
      setIsAiProcessing(false);
    }
  }, []);

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  // Render functions
  const renderWorkspaceTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workspaces.map((workspace) => (
          <div
            key={workspace.id}
            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedWorkspace(workspace.id)}
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <BuildingOfficeIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{workspace.name}</h3>
                <p className="text-sm text-gray-500">{workspace.type}</p>
              </div>
            </div>
            <p className="text-gray-600 text-sm mb-4">{workspace.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <UsersIcon className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-500">{workspace.members.length} members</span>
              </div>
              <div className="flex items-center space-x-1">
                {workspace.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderPagesTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pages.map((page) => (
          <div
            key={page.id}
            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedPage(page.id)}
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <DocumentIcon className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{page.title}</h3>
                <p className="text-sm text-gray-500">{page.type}</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <TimeIcon className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-500">
                  {new Date(page.updatedAt).toLocaleDateString()}
                </span>
              </div>
              <div className="flex items-center space-x-1">
                {page.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderDatabasesTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {databases.map((database) => (
          <div
            key={database.id}
            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedDatabase(database.id)}
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <TableIcon className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{database.title}</h3>
                <p className="text-sm text-gray-500">Database</p>
              </div>
            </div>
            <p className="text-gray-600 text-sm mb-4">{database.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <ChartIcon className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-500">{database.records.length} records</span>
              </div>
              <div className="flex items-center space-x-2">
                <ViewIcon className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-500">{database.views.length} views</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTemplatesTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <div
            key={template.id}
            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => setSelectedTemplate(template.id)}
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                <DocumentDuplicateIcon className="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{template.name}</h3>
                <p className="text-sm text-gray-500">{template.type}</p>
              </div>
            </div>
            <p className="text-gray-600 text-sm mb-4">{template.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <StarIconComponent className="w-4 h-4 text-yellow-400" />
                <span className="text-sm text-gray-500">{template.usageCount} uses</span>
              </div>
              <div className="flex items-center space-x-1">
                {template.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAITab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
            <SparkleIcon className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">AI Assistant</h3>
            <p className="text-sm text-gray-500">Powered by advanced AI</p>
          </div>
        </div>
        
        <div className="space-y-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={aiQuery}
              onChange={(e) => setAiQuery(e.target.value)}
              placeholder="Ask AI anything..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={() => handleAIAssistant(aiQuery)}
              disabled={isAiProcessing || !aiQuery.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAiProcessing ? (
                <ArrowPathIcon className="w-5 h-5 animate-spin" />
              ) : (
                <SparkleIcon className="w-5 h-5" />
              )}
            </button>
          </div>
          
          {aiResponse && (
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-gray-700">{aiResponse}</p>
            </div>
          )}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <ChatIcon className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Conversations</h3>
              <p className="text-sm text-gray-500">{aiAssistant.analytics.totalConversations}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <DocumentDuplicateIcon className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Templates</h3>
              <p className="text-sm text-gray-500">{aiAssistant.analytics.totalTemplates}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <ChartIcon className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Confidence</h3>
              <p className="text-sm text-gray-500">{(aiAssistant.analytics.averageConfidence * 100).toFixed(1)}%</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCollaborationTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <GroupIcon className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Active Sessions</h3>
              <p className="text-2xl font-bold text-blue-600">{collaborativeEditing.activeSessions}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <EditIcon className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Total Operations</h3>
              <p className="text-2xl font-bold text-green-600">{collaborativeEditing.totalOperations}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <ViewIcon className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Active Cursors</h3>
              <p className="text-2xl font-bold text-purple-600">{collaborativeEditing.activeCursors}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <ExclamationIcon className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Conflicts</h3>
              <p className="text-2xl font-bold text-orange-600">{collaborativeEditing.totalConflicts}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Operations by Type</h3>
        <div className="space-y-2">
          {Object.entries(collaborativeEditing.operationsByType).map(([type, count]) => (
            <div key={type} className="flex items-center justify-between">
              <span className="text-sm text-gray-600 capitalize">{type}</span>
              <span className="text-sm font-semibold text-gray-900">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <DocumentIcon className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Total Pages</h3>
              <p className="text-2xl font-bold text-blue-600">{pages.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <TableIcon className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Total Databases</h3>
              <p className="text-2xl font-bold text-green-600">{databaseSystem.totalDatabases}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <DocumentDuplicateIcon className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Total Templates</h3>
              <p className="text-2xl font-bold text-purple-600">{templateSystem.totalTemplates}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <ChartIcon className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Total Records</h3>
              <p className="text-2xl font-bold text-orange-600">{databaseSystem.totalRecords}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Databases by Type</h3>
          <div className="space-y-2">
            {Object.entries(databaseSystem.databasesByType).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">{type}</span>
                <span className="text-sm font-semibold text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Templates by Category</h3>
          <div className="space-y-2">
            {Object.entries(templateSystem.templatesByCategory).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">{category}</span>
                <span className="text-sm font-semibold text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'workspace':
        return renderWorkspaceTab();
      case 'pages':
        return renderPagesTab();
      case 'databases':
        return renderDatabasesTab();
      case 'templates':
        return renderTemplatesTab();
      case 'ai':
        return renderAITab();
      case 'collaboration':
        return renderCollaborationTab();
      case 'analytics':
        return renderAnalyticsTab();
      default:
        return renderWorkspaceTab();
    }
  };

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <SparkleIcon className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Notion-like Dashboard</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="relative">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                placeholder="Search..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <PlusIcon className="w-5 h-5" />
              <span>Create</span>
            </button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200 px-6">
        <nav className="flex space-x-8">
          {[
            { id: 'workspace', label: 'Workspaces', icon: BuildingOfficeIcon },
            { id: 'pages', label: 'Pages', icon: DocumentIcon },
            { id: 'databases', label: 'Databases', icon: TableIcon },
            { id: 'templates', label: 'Templates', icon: DocumentDuplicateIcon },
            { id: 'ai', label: 'AI Assistant', icon: SparkleIcon },
            { id: 'collaboration', label: 'Collaboration', icon: GroupIcon },
            { id: 'analytics', label: 'Analytics', icon: ChartIcon }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id as typeof activeTab)}
              className={`flex items-center space-x-2 px-3 py-4 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="px-6 py-8">
        {renderTabContent()}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Create New {createType}</h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder={`Enter ${createType} name`}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  placeholder={`Enter ${createType} description`}
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotionLikeDashboard;
