import React, { useEffect, useMemo, useState } from 'react';
import { contextApi, nudgeApi } from '../utils/api';

const statusLabels = {
  pending: 'Pending',
  snoozed: 'Snoozed',
  completed: 'Completed',
  dismissed: 'Dismissed',
};

const priorityClasses = {
  low: 'bg-slate-100 text-slate-700',
  medium: 'bg-amber-100 text-amber-800',
  high: 'bg-rose-100 text-rose-800',
};

const initialForm = {
  title: '',
  context: '',
  dueAt: '',
  reminderAt: '',
  priority: 'medium',
};

const initialContextForm = {
  latitude: '',
  longitude: '',
  label: '',
  freeForMinutes: 60,
};

const messyCalendarSample = `Mistral hackathon follow-up notes: met Priya at the Sydney AI meetup. Need to send portfolio tomorrow and follow up next week about the agent demo. Also review project notes before the call with Manoj tomorrow night.`;

const demoGymLocation = {
  latitude: -33.8688,
  longitude: 151.2093,
  label: 'Demo gym location',
};

const farAwayDemoLocation = {
  latitude: -33.8568,
  longitude: 151.2153,
  label: 'Far away demo location',
};

const GEOLOCATION_POLL_MS = 60000;
const RULE_POLL_MS = 60000;
const NOTIFICATION_POLL_MS = 60000;

const getNotificationPermission = () => {
  if (typeof window === 'undefined' || !('Notification' in window)) return 'unsupported';
  return window.Notification.permission;
};

const placeToForm = (place) => ({
  name: place?.name || '',
  latitude: place?.latitude ?? '',
  longitude: place?.longitude ?? '',
  radiusMeters: place?.radiusMeters ?? 300,
  tags: Array.isArray(place?.tags) ? place.tags.join(', ') : '',
  enabled: place?.enabled !== false,
});

const ruleToForm = (rule) => ({
  name: rule?.name || '',
  enabled: rule?.enabled !== false,
  placeId: rule?.placeId || '',
  requiredFreeMinutes: rule?.requiredFreeMinutes ?? 45,
  timeWindowStart: rule?.timeWindow?.start || '06:00',
  timeWindowEnd: rule?.timeWindow?.end || '22:00',
  cooldownMinutes: rule?.cooldownMinutes ?? 360,
  nudgeTitle: rule?.nudgeTemplate?.title || '',
  nudgeContext: rule?.nudgeTemplate?.context || '',
  nudgePriority: rule?.nudgeTemplate?.priority || 'medium',
});

const toInputValue = (value) => {
  if (!value) return '';
  return value.length > 16 ? value.slice(0, 16) : value;
};

const formatDateTime = (value) => {
  if (!value) return 'No due date';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
};

const isDueToday = (nudge) => {
  if (!nudge.dueAt) return false;
  const due = new Date(nudge.dueAt);
  const now = new Date();
  return (
    !Number.isNaN(due.getTime()) &&
    due.getFullYear() === now.getFullYear() &&
    due.getMonth() === now.getMonth() &&
    due.getDate() === now.getDate()
  );
};

const isOverdue = (nudge) => {
  if (!nudge.dueAt || ['completed', 'dismissed'].includes(nudge.status)) return false;
  const due = new Date(nudge.dueAt);
  return !Number.isNaN(due.getTime()) && due < new Date();
};

const NudgeCard = ({ nudge, onStatusChange, onDelete, busy, highlighted }) => {
  const canComplete = nudge.status !== 'completed';
  const canSnooze = nudge.status !== 'snoozed' && nudge.status !== 'completed';
  const canDismiss = nudge.status !== 'dismissed';
  const canReopen = ['completed', 'dismissed', 'snoozed'].includes(nudge.status);

  const snoozeOneDay = () => {
    const next = new Date();
    next.setDate(next.getDate() + 1);
    onStatusChange(nudge.id, {
      status: 'snoozed',
      snoozedUntil: next.toISOString(),
    });
  };

  return (
    <article
      id={`nudge-${nudge.id}`}
      className={`rounded-lg border bg-white p-4 shadow-sm transition-shadow ${highlighted ? 'border-amber-300 ring-2 ring-amber-200' : 'border-gray-200'}`}
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-base font-semibold text-gray-950">{nudge.title}</h3>
            <span className={`rounded-full px-2 py-1 text-xs font-medium ${priorityClasses[nudge.priority] || priorityClasses.medium}`}>
              {nudge.priority}
            </span>
            <span className="rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700">
              {statusLabels[nudge.status] || nudge.status}
            </span>
          </div>
          {nudge.context && <p className="mt-2 text-sm text-gray-600">{nudge.context}</p>}
          <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-500">
            <span>Due: {formatDateTime(nudge.dueAt)}</span>
            {nudge.snoozedUntil && <span>Snoozed until: {formatDateTime(nudge.snoozedUntil)}</span>}
            {nudge.completedAt && <span>Completed: {formatDateTime(nudge.completedAt)}</span>}
          </div>
        </div>
        <div className="flex flex-wrap gap-2 sm:justify-end">
          {canComplete && (
            <button
              type="button"
              disabled={busy}
              onClick={() => onStatusChange(nudge.id, { status: 'completed' })}
              className="rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
            >
              Complete
            </button>
          )}
          {canSnooze && (
            <button
              type="button"
              disabled={busy}
              onClick={snoozeOneDay}
              className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              Snooze
            </button>
          )}
          {canDismiss && (
            <button
              type="button"
              disabled={busy}
              onClick={() => onStatusChange(nudge.id, { status: 'dismissed' })}
              className="rounded-md bg-gray-700 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
            >
              Dismiss
            </button>
          )}
          {canReopen && (
            <button
              type="button"
              disabled={busy}
              onClick={() => onStatusChange(nudge.id, { status: 'pending', snoozedUntil: null })}
              className="rounded-md border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Reopen
            </button>
          )}
          <button
            type="button"
            disabled={busy}
            onClick={() => onDelete(nudge.id)}
            className="rounded-md border border-red-200 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </div>
    </article>
  );
};

const Section = ({ title, nudges, children }) => (
  <section className="space-y-3">
    <div className="flex items-center justify-between">
      <h2 className="text-lg font-semibold text-gray-950">{title}</h2>
      <span className="rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600">
        {nudges.length}
      </span>
    </div>
    {nudges.length === 0 ? (
      <div className="rounded-lg border border-dashed border-gray-300 bg-white p-4 text-sm text-gray-500">
        No nudges in this section.
      </div>
    ) : (
      children
    )}
  </section>
);

const SourceStatusCard = ({ title, status }) => (
  <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
    <div className="flex items-center justify-between gap-3">
      <h3 className="text-sm font-semibold text-gray-950">{title}</h3>
      <span className="rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
        {status?.status || 'unknown'}
      </span>
    </div>
    <p className="mt-2 text-sm text-gray-600">{status?.message || 'No source status available.'}</p>
    {status?.freeForMinutes !== undefined && (
      <p className="mt-2 text-xs text-gray-500">Free for: {status.freeForMinutes} minutes</p>
    )}
  </div>
);

const Modal = ({ title, onClose, children }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-950/50 p-4">
    <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white shadow-xl">
      <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4">
        <h2 className="text-lg font-semibold text-gray-950">{title}</h2>
        <button
          type="button"
          onClick={onClose}
          className="rounded-md border border-gray-300 px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Close
        </button>
      </div>
      {children}
    </div>
  </div>
);

const PlaceEditModal = ({ place, onClose, onSave, busy }) => {
  const [form, setForm] = useState(() => placeToForm(place));
  const [localError, setLocalError] = useState('');

  const submit = (event) => {
    event.preventDefault();
    const latitude = Number(form.latitude);
    const longitude = Number(form.longitude);
    const radiusMeters = Number(form.radiusMeters);
    if (!form.name.trim() || Number.isNaN(latitude) || Number.isNaN(longitude) || Number.isNaN(radiusMeters)) {
      setLocalError('Name, latitude, longitude, and radius must be valid.');
      return;
    }

    setLocalError('');
    onSave({
      name: form.name.trim(),
      latitude,
      longitude,
      radiusMeters,
      tags: form.tags.split(',').map((tag) => tag.trim()).filter(Boolean),
      enabled: form.enabled,
    });
  };

  return (
    <Modal title={`Edit ${place.name}`} onClose={onClose}>
      <form onSubmit={submit} className="space-y-4 p-5">
        {localError && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{localError}</div>}
        <label className="block">
          <span className="text-sm font-medium text-gray-700">Name</span>
          <input
            value={form.name}
            onChange={(event) => setForm({ ...form, name: event.target.value })}
            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </label>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <label>
            <span className="text-sm font-medium text-gray-700">Latitude</span>
            <input
              type="number"
              step="0.000001"
              value={form.latitude}
              onChange={(event) => setForm({ ...form, latitude: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Longitude</span>
            <input
              type="number"
              step="0.000001"
              value={form.longitude}
              onChange={(event) => setForm({ ...form, longitude: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Radius meters</span>
            <input
              type="number"
              min="1"
              max="100000"
              value={form.radiusMeters}
              onChange={(event) => setForm({ ...form, radiusMeters: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
        </div>
        <label className="block">
          <span className="text-sm font-medium text-gray-700">Tags</span>
          <input
            value={form.tags}
            onChange={(event) => setForm({ ...form, tags: event.target.value })}
            placeholder="fitness, personal"
            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={form.enabled}
            onChange={(event) => setForm({ ...form, enabled: event.target.checked })}
            className="h-4 w-4 rounded border-gray-300"
          />
          Enabled
        </label>
        <div className="flex justify-end gap-3 border-t border-gray-200 pt-4">
          <button type="button" onClick={onClose} className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
            Cancel
          </button>
          <button type="submit" disabled={busy} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
            {busy ? 'Saving...' : 'Save Place'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

const RuleEditModal = ({ rule, places, onClose, onSave, busy }) => {
  const [form, setForm] = useState(() => ruleToForm(rule));
  const [localError, setLocalError] = useState('');

  const submit = (event) => {
    event.preventDefault();
    const requiredFreeMinutes = Number(form.requiredFreeMinutes);
    const cooldownMinutes = Number(form.cooldownMinutes);
    if (!form.name.trim() || !form.placeId || Number.isNaN(requiredFreeMinutes) || Number.isNaN(cooldownMinutes)) {
      setLocalError('Name, place, free minutes, and cooldown must be valid.');
      return;
    }

    setLocalError('');
    onSave({
      name: form.name.trim(),
      enabled: form.enabled,
      placeId: form.placeId,
      requiredFreeMinutes,
      timeWindow: { start: form.timeWindowStart, end: form.timeWindowEnd },
      cooldownMinutes,
      nudgeTemplate: {
        title: form.nudgeTitle.trim() || form.name.trim(),
        context: form.nudgeContext.trim(),
        priority: form.nudgePriority,
      },
    });
  };

  return (
    <Modal title={`Edit ${rule.name}`} onClose={onClose}>
      <form onSubmit={submit} className="space-y-4 p-5">
        {localError && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{localError}</div>}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <label>
            <span className="text-sm font-medium text-gray-700">Rule name</span>
            <input
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Place</span>
            <select
              value={form.placeId}
              onChange={(event) => setForm({ ...form, placeId: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            >
              {places.map((place) => (
                <option key={place.id} value={place.id}>{place.name}</option>
              ))}
            </select>
          </label>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <label>
            <span className="text-sm font-medium text-gray-700">Free minutes</span>
            <input
              type="number"
              min="0"
              max="1440"
              value={form.requiredFreeMinutes}
              onChange={(event) => setForm({ ...form, requiredFreeMinutes: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Window start</span>
            <input
              type="time"
              value={form.timeWindowStart}
              onChange={(event) => setForm({ ...form, timeWindowStart: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Window end</span>
            <input
              type="time"
              value={form.timeWindowEnd}
              onChange={(event) => setForm({ ...form, timeWindowEnd: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Cooldown minutes</span>
            <input
              type="number"
              min="0"
              max="43200"
              value={form.cooldownMinutes}
              onChange={(event) => setForm({ ...form, cooldownMinutes: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
        </div>
        <label className="block">
          <span className="text-sm font-medium text-gray-700">Nudge title</span>
          <input
            value={form.nudgeTitle}
            onChange={(event) => setForm({ ...form, nudgeTitle: event.target.value })}
            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-gray-700">Nudge context</span>
          <textarea
            rows={3}
            value={form.nudgeContext}
            onChange={(event) => setForm({ ...form, nudgeContext: event.target.value })}
            className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </label>
        <div className="flex flex-wrap items-center gap-4">
          <label>
            <span className="text-sm font-medium text-gray-700">Priority</span>
            <select
              value={form.nudgePriority}
              onChange={(event) => setForm({ ...form, nudgePriority: event.target.value })}
              className="ml-2 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={form.enabled}
              onChange={(event) => setForm({ ...form, enabled: event.target.checked })}
              className="h-4 w-4 rounded border-gray-300"
            />
            Enabled
          </label>
        </div>
        <div className="flex justify-end gap-3 border-t border-gray-200 pt-4">
          <button type="button" onClick={onClose} className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
            Cancel
          </button>
          <button type="submit" disabled={busy} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
            {busy ? 'Saving...' : 'Save Rule'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

const Dashboard = () => {
  const [nudges, setNudges] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState('');
  const [contextState, setContextState] = useState(null);
  const [contextForm, setContextForm] = useState(initialContextForm);
  const [contextBusy, setContextBusy] = useState(false);
  const [contextMessage, setContextMessage] = useState('');
  const [browserLocationEnabled, setBrowserLocationEnabled] = useState(false);
  const [rulePollingEnabled, setRulePollingEnabled] = useState(false);
  const [automationMessage, setAutomationMessage] = useState('');
  const [editingPlace, setEditingPlace] = useState(null);
  const [editingRule, setEditingRule] = useState(null);
  const [editorBusy, setEditorBusy] = useState(false);
  const [extractText, setExtractText] = useState('');
  const [extractSuggestions, setExtractSuggestions] = useState([]);
  const [extracting, setExtracting] = useState(false);
  const [extractError, setExtractError] = useState('');
  const [extractMessage, setExtractMessage] = useState('');
  const [approvingSuggestionId, setApprovingSuggestionId] = useState(null);
  const [desktopNotificationsEnabled, setDesktopNotificationsEnabled] = useState(false);
  const [notificationPermission, setNotificationPermission] = useState(getNotificationPermission);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [highlightedNudgeId, setHighlightedNudgeId] = useState(null);

  const loadNudges = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await nudgeApi.list();
      setNudges(response.data.nudges || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not load nudges. Check that the backend is running on port 8001.');
    } finally {
      setLoading(false);
    }
  };

  const loadContext = async () => {
    try {
      const response = await contextApi.get();
      const nextState = response.data;
      setContextState(nextState);
      setContextForm({
        latitude: nextState.currentLocation?.latitude ?? '',
        longitude: nextState.currentLocation?.longitude ?? '',
        label: nextState.currentLocation?.label ?? '',
        freeForMinutes: nextState.calendar?.freeForMinutes ?? 60,
      });
    } catch (err) {
      setContextMessage('Context rules are unavailable. Check that the backend is running.');
    }
  };

  const addNudgeIfMissing = (nudge) => {
    setNudges((current) => (current.some((item) => item.id === nudge.id) ? current : [...current, nudge]));
  };

  const focusNudge = (id) => {
    if (!id || typeof window === 'undefined') return;
    window.focus();
    setHighlightedNudgeId(id);
    window.setTimeout(() => {
      document.getElementById(`nudge-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 50);
    window.setTimeout(() => setHighlightedNudgeId(null), 7000);
  };

  const requestDesktopNotifications = async () => {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      setNotificationPermission('unsupported');
      setDesktopNotificationsEnabled(false);
      setNotificationMessage('Desktop notifications are not supported in this browser.');
      return;
    }

    if (window.Notification.permission === 'granted') {
      setNotificationPermission('granted');
      setDesktopNotificationsEnabled(true);
      setNotificationMessage('Desktop notifications enabled.');
      return;
    }

    const permission = await window.Notification.requestPermission();
    setNotificationPermission(permission);
    setDesktopNotificationsEnabled(permission === 'granted');
    setNotificationMessage(
      permission === 'granted'
        ? 'Desktop notifications enabled.'
        : 'Desktop notification permission was not granted.'
    );
  };

  const pollNotificationAlerts = async () => {
    if (!desktopNotificationsEnabled || getNotificationPermission() !== 'granted') return;

    try {
      const response = await contextApi.pollNotifications();
      const alerts = Array.isArray(response.data) ? response.data : [];
      alerts.forEach((alert) => {
        const notification = new window.Notification(alert.title, {
          body: alert.body,
          tag: `nudge-${alert.id}`,
        });
        notification.onclick = () => focusNudge(alert.id);
      });
      if (alerts.length > 0) {
        setNotificationMessage(`Sent ${alerts.length} desktop alert${alerts.length === 1 ? '' : 's'}.`);
      }
    } catch (err) {
      setNotificationMessage(err.response?.data?.error?.message || 'Could not poll desktop alerts.');
    }
  };

  const fetchBrowserLocation = (successMessage = 'Browser location updated.') => {
    if (!navigator.geolocation) {
      setAutomationMessage('Browser geolocation is not available in this browser.');
      setBrowserLocationEnabled(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const payload = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracyMeters: position.coords.accuracy,
          source: 'browser',
          label: 'Browser location while app is open',
        };

        try {
          const response = await contextApi.updateLocation(payload);
          setContextState((current) => ({
            ...(current || {}),
            currentLocation: response.data.currentLocation,
            sourceStatus: response.data.sourceStatus || current?.sourceStatus,
          }));
          setContextForm((current) => ({
            ...current,
            latitude: payload.latitude,
            longitude: payload.longitude,
            label: payload.label,
          }));
          setAutomationMessage(successMessage);
        } catch (err) {
          setAutomationMessage(err.response?.data?.error?.message || 'Could not save browser location.');
        }
      },
      (geoError) => {
        setAutomationMessage(geoError.message || 'Browser location permission was denied or unavailable.');
        setBrowserLocationEnabled(false);
      },
      { enableHighAccuracy: false, maximumAge: 60000, timeout: 10000 }
    );
  };

  const pollContextRules = async (successPrefix = 'Context rules checked') => {
    try {
      const response = await contextApi.evaluate();
      if (response.data.created && response.data.nudge) {
        addNudgeIfMissing(response.data.nudge);
        setAutomationMessage(`${successPrefix}: created ${response.data.nudge.title}.`);
        await pollNotificationAlerts();
      } else {
        const reason = response.data.evaluations?.[0]?.reasons?.[0] || 'no rule matched.';
        setAutomationMessage(`${successPrefix}: ${reason}`);
      }
      setContextState((current) => ({
        ...(current || {}),
        sourceStatus: response.data.sourceStatus || current?.sourceStatus,
      }));
    } catch (err) {
      setAutomationMessage(err.response?.data?.error?.message || 'Could not poll context rules.');
    }
  };

  useEffect(() => {
    loadNudges();
    loadContext();
  }, []);

  useEffect(() => {
    if (!browserLocationEnabled) return undefined;

    fetchBrowserLocation('Browser location polling started.');
    const timerId = window.setInterval(() => {
      fetchBrowserLocation('Browser location refreshed.');
    }, GEOLOCATION_POLL_MS);

    return () => window.clearInterval(timerId);
  }, [browserLocationEnabled]);

  useEffect(() => {
    if (!rulePollingEnabled) return undefined;

    pollContextRules('Context rule polling started');
    const timerId = window.setInterval(() => {
      pollContextRules('Context rule polling');
    }, RULE_POLL_MS);

    return () => window.clearInterval(timerId);
  }, [rulePollingEnabled, desktopNotificationsEnabled, notificationPermission]);

  useEffect(() => {
    if (!desktopNotificationsEnabled || notificationPermission !== 'granted') return undefined;

    pollNotificationAlerts();
    const timerId = window.setInterval(() => {
      pollNotificationAlerts();
    }, NOTIFICATION_POLL_MS);

    return () => window.clearInterval(timerId);
  }, [desktopNotificationsEnabled, notificationPermission]);

  const grouped = useMemo(() => {
    const active = nudges.filter((nudge) => !['completed', 'dismissed'].includes(nudge.status));
    return {
      overdue: active.filter(isOverdue),
      dueToday: active.filter((nudge) => isDueToday(nudge) && !isOverdue(nudge)),
      pending: nudges.filter((nudge) => nudge.status === 'pending' && !isDueToday(nudge) && !isOverdue(nudge)),
      snoozed: nudges.filter((nudge) => nudge.status === 'snoozed'),
      completed: nudges.filter((nudge) => nudge.status === 'completed'),
      dismissed: nudges.filter((nudge) => nudge.status === 'dismissed'),
    };
  }, [nudges]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!form.title.trim()) {
      setError('Title is required.');
      return;
    }

    setSaving(true);
    setError('');
    try {
      const payload = {
        title: form.title.trim(),
        context: form.context.trim() || null,
        dueAt: form.dueAt ? new Date(form.dueAt).toISOString() : null,
        reminderAt: form.reminderAt ? new Date(form.reminderAt).toISOString() : null,
        priority: form.priority,
      };
      const response = await nudgeApi.create(payload);
      setNudges((current) => [...current, response.data.nudge]);
      setForm(initialForm);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not create nudge.');
    } finally {
      setSaving(false);
    }
  };

  const handleExtractNudges = async () => {
    if (!extractText.trim()) {
      setExtractError('Paste notes or load the sample before extracting.');
      return;
    }

    setExtracting(true);
    setExtractError('');
    setExtractMessage('');
    try {
      const response = await contextApi.extractNudges(extractText.trim());
      const suggestions = (response.data.suggestions || []).map((suggestion, index) => ({
        ...suggestion,
        reviewId: `${Date.now()}-${index}`,
      }));
      setExtractSuggestions(suggestions);
      setExtractMessage(
        suggestions.length > 0
          ? `Found ${suggestions.length} suggestion${suggestions.length === 1 ? '' : 's'} using ${response.data.source || 'extractor'}.`
          : 'No actionable nudges found. Try adding dates, people, or action verbs.'
      );
    } catch (err) {
      setExtractError(err.response?.data?.error?.message || 'Could not extract nudges from this text.');
    } finally {
      setExtracting(false);
    }
  };

  const approveSuggestion = async (suggestion) => {
    setApprovingSuggestionId(suggestion.reviewId);
    setExtractError('');
    try {
      const contextParts = [
        suggestion.ai_note ? `Source: ${suggestion.ai_note}` : null,
        suggestion.reasoning ? `Reason: ${suggestion.reasoning}` : null,
      ].filter(Boolean);
      const response = await nudgeApi.create({
        title: suggestion.title,
        context: contextParts.join('\n') || null,
        dueAt: suggestion.due_date || null,
        reminderAt: suggestion.due_date || null,
        priority: suggestion.confidence_score >= 0.75 ? 'high' : 'medium',
      });
      setNudges((current) => [...current, response.data.nudge]);
      setExtractSuggestions((current) => current.filter((item) => item.reviewId !== suggestion.reviewId));
      setExtractMessage('Suggestion approved and saved as a normal nudge.');
    } catch (err) {
      setExtractError(err.response?.data?.error?.message || 'Could not save this suggestion.');
    } finally {
      setApprovingSuggestionId(null);
    }
  };

  const dismissSuggestion = (reviewId) => {
    setExtractSuggestions((current) => current.filter((item) => item.reviewId !== reviewId));
    setExtractMessage('Suggestion dismissed.');
  };

  const updateNudge = async (id, payload) => {
    setBusyId(id);
    setError('');
    try {
      const response = await nudgeApi.update(id, payload);
      setNudges((current) => current.map((nudge) => (nudge.id === id ? response.data.nudge : nudge)));
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not update nudge.');
    } finally {
      setBusyId(null);
    }
  };

  const deleteNudge = async (id) => {
    setBusyId(id);
    setError('');
    try {
      await nudgeApi.remove(id);
      setNudges((current) => current.filter((nudge) => nudge.id !== id));
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not delete nudge.');
    } finally {
      setBusyId(null);
    }
  };

  const saveContextInputs = async () => {
    const latitude = Number(contextForm.latitude);
    const longitude = Number(contextForm.longitude);
    const freeForMinutes = Number(contextForm.freeForMinutes);
    if (Number.isNaN(latitude) || Number.isNaN(longitude) || Number.isNaN(freeForMinutes)) {
      setContextMessage('Location and free minutes must be valid numbers.');
      return;
    }

    setContextBusy(true);
    setContextMessage('');
    try {
      await contextApi.updateLocation({
        latitude,
        longitude,
        source: 'manual',
        label: contextForm.label || 'Manual location',
      });
      await contextApi.updateCalendar({
        mode: 'manual',
        freeForMinutes,
        message: `Manual calendar availability: free for ${freeForMinutes} minutes.`,
      });
      await loadContext();
      setContextMessage('Context inputs saved.');
    } catch (err) {
      setContextMessage(err.response?.data?.error?.message || 'Could not save context inputs.');
    } finally {
      setContextBusy(false);
    }
  };

  const savePlaceEdit = async (payload) => {
    if (!editingPlace) return;
    setEditorBusy(true);
    setContextMessage('');
    try {
      await contextApi.updatePlace(editingPlace.id, payload);
      await loadContext();
      setEditingPlace(null);
      setContextMessage('Place updated.');
    } catch (err) {
      setContextMessage(err.response?.data?.error?.message || 'Could not update place.');
    } finally {
      setEditorBusy(false);
    }
  };

  const saveRuleEdit = async (payload) => {
    if (!editingRule) return;
    setEditorBusy(true);
    setContextMessage('');
    try {
      await contextApi.updateRule(editingRule.id, payload);
      await loadContext();
      setEditingRule(null);
      setContextMessage('Context rule updated.');
    } catch (err) {
      setContextMessage(err.response?.data?.error?.message || 'Could not update context rule.');
    } finally {
      setEditorBusy(false);
    }
  };

  const useDemoLocation = (location) => {
    setContextForm((current) => ({
      ...current,
      latitude: location.latitude,
      longitude: location.longitude,
      label: location.label,
    }));
  };

  const evaluateGymRule = async () => {
    setContextBusy(true);
    setContextMessage('');
    try {
      const response = await contextApi.evaluate();
      if (response.data.created && response.data.nudge) {
        addNudgeIfMissing(response.data.nudge);
        setContextMessage('Gym Opportunity matched and created a nudge.');
      } else {
        const reason = response.data.evaluations?.[0]?.reasons?.[0] || 'Gym Opportunity did not match.';
        setContextMessage(reason);
      }
      await loadContext();
    } catch (err) {
      setContextMessage(err.response?.data?.error?.message || 'Could not evaluate context rules.');
    } finally {
      setContextBusy(false);
    }
  };

  const renderCards = (items) =>
    items.map((nudge) => (
      <NudgeCard
        key={nudge.id}
        nudge={nudge}
        onStatusChange={updateNudge}
        onDelete={deleteNudge}
        busy={busyId === nudge.id}
        highlighted={highlightedNudgeId === nudge.id}
      />
    ));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-950">Nudge Dashboard</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manual nudge MVP. Data integrations and AI tools are experimental until the core loop is stable.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-950">Create Nudge</h2>
        <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-4">
          <label className="lg:col-span-2">
            <span className="text-sm font-medium text-gray-700">Title</span>
            <input
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              placeholder="Follow up with Priya"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Due</span>
            <input
              type="datetime-local"
              value={toInputValue(form.dueAt)}
              onChange={(event) => setForm({ ...form, dueAt: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Priority</span>
            <select
              value={form.priority}
              onChange={(event) => setForm({ ...form, priority: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label className="lg:col-span-3">
            <span className="text-sm font-medium text-gray-700">Context</span>
            <textarea
              value={form.context}
              onChange={(event) => setForm({ ...form, context: event.target.value })}
              rows={3}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              placeholder="Add the source note, person, or reason this matters."
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Reminder</span>
            <input
              type="datetime-local"
              value={toInputValue(form.reminderAt)}
              onChange={(event) => setForm({ ...form, reminderAt: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
        </div>
        <div className="mt-4 flex items-center gap-3">
          <button
            type="submit"
            disabled={saving}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Create Nudge'}
          </button>
          <button
            type="button"
            onClick={loadNudges}
            disabled={loading}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Refresh
          </button>
        </div>
      </form>

      <section className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold text-gray-950">Messy Review</h2>
          <p className="text-sm text-gray-600">
            Paste raw notes or calendar text. Suggestions stay in pending review until you approve them.
          </p>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
          <label>
            <span className="text-sm font-medium text-gray-700">Raw text</span>
            <textarea
              value={extractText}
              onChange={(event) => setExtractText(event.target.value)}
              rows={7}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
              placeholder="Paste meeting notes, clipboard text, or a messy calendar description."
            />
          </label>
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
            <h3 className="text-sm font-semibold text-gray-950">Extraction Guardrails</h3>
            <p className="mt-2 text-sm text-gray-600">
              The backend returns drafts only. Nothing is saved until you approve a suggestion.
            </p>
            <p className="mt-2 text-sm text-gray-600">
              If no LLM is configured, NudgeAI uses local rule-based parsing.
            </p>
            <div className="mt-4 flex flex-col gap-2">
              <button
                type="button"
                onClick={() => setExtractText(messyCalendarSample)}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Load Sample Text
              </button>
              <button
                type="button"
                onClick={handleExtractNudges}
                disabled={extracting}
                className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
              >
                {extracting ? 'Extracting...' : 'Extract Suggestions'}
              </button>
            </div>
          </div>
        </div>

        {extractError && (
          <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {extractError}
          </div>
        )}
        {extractMessage && !extractError && (
          <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
            {extractMessage}
          </div>
        )}

        <div className="mt-5">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-950">Pending Review</h3>
            <span className="rounded-full bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600">
              {extractSuggestions.length}
            </span>
          </div>
          {extractSuggestions.length === 0 ? (
            <div className="mt-3 rounded-lg border border-dashed border-gray-300 bg-gray-50 p-4 text-sm text-gray-500">
              Extracted suggestions will appear here before they become saved nudges.
            </div>
          ) : (
            <div className="mt-3 space-y-3">
              {extractSuggestions.map((suggestion) => {
                const confidence = Math.round((Number(suggestion.confidence_score) || 0) * 100);
                return (
                  <article key={suggestion.reviewId} className="rounded-lg border border-gray-200 bg-gray-50 p-4">
                    <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <h4 className="text-base font-semibold text-gray-950">{suggestion.title}</h4>
                          <span className="rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">
                            {confidence}% confidence
                          </span>
                        </div>
                        <p className="mt-2 text-sm text-gray-600">Due: {formatDateTime(suggestion.due_date)}</p>
                        <p className="mt-2 text-sm text-gray-700">{suggestion.reasoning}</p>
                        {suggestion.ai_note && <p className="mt-2 text-xs text-gray-500">Source: {suggestion.ai_note}</p>}
                      </div>
                      <div className="flex flex-wrap gap-2 lg:justify-end">
                        <button
                          type="button"
                          onClick={() => approveSuggestion(suggestion)}
                          disabled={approvingSuggestionId === suggestion.reviewId}
                          className="rounded-md bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
                        >
                          {approvingSuggestionId === suggestion.reviewId ? 'Saving...' : 'Quick Approve'}
                        </button>
                        <button
                          type="button"
                          onClick={() => dismissSuggestion(suggestion.reviewId)}
                          disabled={approvingSuggestionId === suggestion.reviewId}
                          className="rounded-md border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-white disabled:opacity-50"
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </div>
      </section>

      <section className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold text-gray-950">Personal Context Rules</h2>
          <p className="text-sm text-gray-600">
            Local debug controls for the Gym Opportunity rule. This uses manual location and free/busy inputs.
          </p>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
          <SourceStatusCard title="Location" status={contextState?.sourceStatus?.location} />
          <SourceStatusCard title="Calendar" status={contextState?.sourceStatus?.calendar} />
        </div>

        <div className="mt-4 rounded-lg border border-blue-100 bg-blue-50 p-4">
          <div className="flex flex-col gap-1">
            <h3 className="text-sm font-semibold text-blue-950">Local Automation</h3>
            <p className="text-sm text-blue-800">
              Optional browser-only loops. They run while this dashboard is open and write only to ignored local JSON stores.
            </p>
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-blue-950">
              <input
                type="checkbox"
                checked={browserLocationEnabled}
                onChange={(event) => setBrowserLocationEnabled(event.target.checked)}
                className="h-4 w-4 rounded border-blue-300"
              />
              Poll browser location every 60s
            </label>
            <label className="flex items-center gap-2 text-sm text-blue-950">
              <input
                type="checkbox"
                checked={rulePollingEnabled}
                onChange={(event) => setRulePollingEnabled(event.target.checked)}
                className="h-4 w-4 rounded border-blue-300"
              />
              Poll context rules every 60s
            </label>
            <button
              type="button"
              onClick={() => fetchBrowserLocation('Browser location fetched once.')}
              className="rounded-md border border-blue-200 bg-white px-3 py-2 text-sm font-medium text-blue-800 hover:bg-blue-100"
            >
              Use Browser Location Once
            </button>
            {desktopNotificationsEnabled ? (
              <button
                type="button"
                onClick={() => {
                  setDesktopNotificationsEnabled(false);
                  setNotificationMessage('Desktop notifications paused for this dashboard.');
                }}
                className="rounded-md border border-blue-200 bg-white px-3 py-2 text-sm font-medium text-blue-800 hover:bg-blue-100"
              >
                Disable Desktop Notifications
              </button>
            ) : (
              <button
                type="button"
                onClick={requestDesktopNotifications}
                className="rounded-md bg-blue-700 px-3 py-2 text-sm font-medium text-white hover:bg-blue-800"
              >
                Enable Desktop Notifications
              </button>
            )}
          </div>
          {automationMessage && <p className="mt-3 text-sm text-blue-800">{automationMessage}</p>}
          <p className="mt-2 text-sm text-blue-800">
            Notification permission: {notificationPermission}.
          </p>
          {notificationMessage && <p className="mt-2 text-sm text-blue-800">{notificationMessage}</p>}
        </div>

        <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-4">
          <label>
            <span className="text-sm font-medium text-gray-700">Latitude</span>
            <input
              type="number"
              step="0.000001"
              value={contextForm.latitude}
              onChange={(event) => setContextForm({ ...contextForm, latitude: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Longitude</span>
            <input
              type="number"
              step="0.000001"
              value={contextForm.longitude}
              onChange={(event) => setContextForm({ ...contextForm, longitude: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Location label</span>
            <input
              value={contextForm.label}
              onChange={(event) => setContextForm({ ...contextForm, label: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label>
            <span className="text-sm font-medium text-gray-700">Free minutes</span>
            <input
              type="number"
              min="0"
              max="1440"
              value={contextForm.freeForMinutes}
              onChange={(event) => setContextForm({ ...contextForm, freeForMinutes: event.target.value })}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => useDemoLocation(demoGymLocation)}
            className="rounded-md border border-emerald-200 px-4 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50"
          >
            Use Demo Gym Location
          </button>
          <button
            type="button"
            onClick={() => useDemoLocation(farAwayDemoLocation)}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Use Far Away Demo
          </button>
          <button
            type="button"
            onClick={saveContextInputs}
            disabled={contextBusy}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Save Context
          </button>
          <button
            type="button"
            onClick={evaluateGymRule}
            disabled={contextBusy}
            className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
          >
            Check Context Rules Now
          </button>
          {contextMessage && <span className="text-sm text-gray-600">{contextMessage}</span>}
        </div>

        <div className="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-sm font-semibold text-gray-950">Places</h3>
              <span className="rounded-full bg-white px-2 py-1 text-xs font-medium text-gray-600">
                {contextState?.places?.length || 0}
              </span>
            </div>
            <div className="mt-3 space-y-3">
              {(contextState?.places || []).map((place) => (
                <div key={place.id} className="rounded-md border border-gray-200 bg-white p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-gray-950">{place.name}</p>
                      <p className="mt-1 text-xs text-gray-500">
                        Radius {place.radiusMeters}m - {place.enabled ? 'enabled' : 'disabled'}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setEditingPlace(place)}
                      className="rounded-md border border-gray-300 px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Edit
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-sm font-semibold text-gray-950">Context Rules</h3>
              <span className="rounded-full bg-white px-2 py-1 text-xs font-medium text-gray-600">
                {contextState?.rules?.length || 0}
              </span>
            </div>
            <div className="mt-3 space-y-3">
              {(contextState?.rules || []).map((rule) => (
                <div key={rule.id} className="rounded-md border border-gray-200 bg-white p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-gray-950">{rule.name}</p>
                      <p className="mt-1 text-xs text-gray-500">
                        Needs {rule.requiredFreeMinutes} free minutes - cooldown {rule.cooldownMinutes}m - {rule.enabled ? 'enabled' : 'disabled'}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setEditingRule(rule)}
                      className="rounded-md border border-gray-300 px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Edit
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {loading ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-600">
          Loading nudges...
        </div>
      ) : nudges.length === 0 ? (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center">
          <h2 className="text-lg font-semibold text-gray-950">No nudges yet</h2>
          <p className="mt-1 text-sm text-gray-600">Create your first manual nudge to start the MVP loop.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <Section title="Overdue" nudges={grouped.overdue}>{renderCards(grouped.overdue)}</Section>
          <Section title="Due Today" nudges={grouped.dueToday}>{renderCards(grouped.dueToday)}</Section>
          <Section title="Pending" nudges={grouped.pending}>{renderCards(grouped.pending)}</Section>
          <Section title="Snoozed" nudges={grouped.snoozed}>{renderCards(grouped.snoozed)}</Section>
          <Section title="Completed" nudges={grouped.completed}>{renderCards(grouped.completed)}</Section>
          <Section title="Dismissed" nudges={grouped.dismissed}>{renderCards(grouped.dismissed)}</Section>
        </div>
      )}

      {editingPlace && (
        <PlaceEditModal
          key={editingPlace.id}
          place={editingPlace}
          onClose={() => setEditingPlace(null)}
          onSave={savePlaceEdit}
          busy={editorBusy}
        />
      )}

      {editingRule && (
        <RuleEditModal
          key={editingRule.id}
          rule={editingRule}
          places={contextState?.places || []}
          onClose={() => setEditingRule(null)}
          onSave={saveRuleEdit}
          busy={editorBusy}
        />
      )}
    </div>
  );
};

export default Dashboard;
