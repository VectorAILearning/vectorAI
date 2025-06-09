import { useEffect, useState } from "react";
import React from "react";
import CopyButton from "../components/CopyButton";
import { HiChevronDown, HiChevronRight } from "react-icons/hi";

export type TaskOut = {
  id: string;
  parent_id?: string | null;
  task_type: string;
  params?: any;
  status: string;
  result?: any;
  session_id?: string | null;
  user_id?: string | null;
  error_message?: string | null;
  created_at?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
};

function buildTaskTree(tasks: TaskOut[]) {
  const map: Record<string, TaskOut & { children?: TaskOut[] }> = {};
  const roots: (TaskOut & { children?: TaskOut[] })[] = [];
  tasks.forEach((task) => {
    map[task.id] = { ...task, children: [] };
  });
  tasks.forEach((task) => {
    if (task.parent_id && map[task.parent_id]) {
      map[task.parent_id].children!.push(map[task.id]);
    } else {
      roots.push(map[task.id]);
    }
  });
  return roots;
}

function getDuration(started_at?: string | null, finished_at?: string | null) {
  if (!started_at || !finished_at) return "-";
  const start = new Date(started_at).getTime();
  const end = new Date(finished_at).getTime();
  if (isNaN(start) || isNaN(end) || end < start) return "-";
  const diffSec = Math.floor((end - start) / 1000);
  if (diffSec < 60) return `${diffSec} сек.`;
  const min = Math.floor(diffSec / 60);
  const sec = diffSec % 60;
  return `${min} мин. ${sec} сек.`;
}

function expandAllChildren(
  task: TaskOut & { children?: TaskOut[] },
  expanded: Record<string, boolean>,
): Record<string, boolean> {
  let result = { ...expanded, [task.id]: true };
  if (task.children && task.children.length > 0) {
    for (const child of task.children) {
      result = expandAllChildren(child, result);
    }
  }
  return result;
}

function getStatusClass(status: string) {
  switch (status) {
    case "success":
      return "text-success font-bold";
    case "pending":
      return "text-warning font-bold";
    case "in_progress":
      return "text-orange-500 font-bold";
    case "failed":
      return "text-error font-bold";
    default:
      return "";
  }
}

function formatJson(value: any) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

function shortId(id: string) {
  if (!id || id.length < 12) return id;
  return id.slice(0, 6) + "..." + id.slice(-4);
}

function shortValue(val: any) {
  if (val == null) return "-";
  let str = "";
  if (typeof val === "string") {
    str = val;
  } else if (typeof val === "object") {
    str = JSON.stringify(val);
  } else {
    str = String(val);
  }
  if (str.length > 15) {
    return str.slice(0, 8) + "…" + str.slice(-5);
  }
  return str;
}

function TaskTableRows({
  tasks,
  level = 0,
  expanded,
  toggleExpand,
}: {
  tasks: (TaskOut & { children?: TaskOut[] })[];
  level?: number;
  expanded: Record<string, boolean>;
  toggleExpand: (task: TaskOut & { children?: TaskOut[] }) => void;
}) {
  return (
    <>
      {tasks.map((task) => {
        const hasChildren = task.children && task.children.length > 0;
        const isExpanded = expanded[task.id];
        const row = (
          <tr key={`row-${task.id}`}>
            <td
              style={{ paddingLeft: level * 3 }}
              className="whitespace-nowrap"
            >
              {hasChildren && (
                <button
                  className="btn btn-xs btn-ghost text-base-content"
                  onClick={() => toggleExpand(task)}
                  title={isExpanded ? "Свернуть" : "Развернуть"}
                >
                  {isExpanded ? (
                    <HiChevronDown className="inline w-4 h-4" />
                  ) : (
                    <HiChevronRight className="inline w-4 h-4" />
                  )}
                </button>
              )}
              <span className="font-semibold">{task.task_type}</span>
            </td>
            <td className="text-xs" title={task.id}>
              <span className="inline-flex items-center gap-1">
                <span>{shortId(task.id)}</span>
                <CopyButton value={task.id} title="Скопировать id" />
              </span>
            </td>
            <td className={getStatusClass(task.status)}>{task.status}</td>
            <td className="text-xs text-base-content/60">
              {task.created_at
                ? new Date(task.created_at).toLocaleString()
                : "-"}
            </td>
            <td className="text-xs text-base-content/60">
              {task.started_at
                ? new Date(task.started_at).toLocaleString()
                : "-"}
            </td>
            <td className="text-xs text-base-content/60">
              {task.finished_at
                ? new Date(task.finished_at).toLocaleString()
                : "-"}
            </td>
            <td>{getDuration(task.started_at, task.finished_at)}</td>
            <td>
              {(task.error_message && (
                <span className="text-error">{task.error_message}</span>
              )) ||
                "-"}
            </td>
            <td>
              <span className="inline-flex items-center gap-1">
                <span>{task.session_id ? shortId(task.session_id) : "-"}</span>
                {task.session_id && (
                  <CopyButton value={task.session_id} title="Скопировать id" />
                )}
              </span>
            </td>
            <td>
              <span className="inline-flex items-center gap-1">
                <span>{task.user_id ? shortId(task.user_id) : "-"}</span>
                {task.user_id && (
                  <CopyButton value={task.user_id} title="Скопировать id" />
                )}
              </span>
            </td>
            <td
              title={
                task.params
                  ? typeof task.params === "string"
                    ? task.params
                    : formatJson(task.params)
                  : ""
              }
            >
              <span className="inline-flex items-center gap-1">
                {task.params ? shortValue(task.params) : "-"}
                {task.params && (
                  <CopyButton
                    value={
                      typeof task.params === "string"
                        ? task.params
                        : formatJson(task.params)
                    }
                    title="Скопировать параметры"
                  />
                )}
              </span>
            </td>
            <td
              title={
                task.result
                  ? typeof task.result === "string"
                    ? task.result
                    : formatJson(task.result)
                  : ""
              }
            >
              <span className="inline-flex items-center gap-1">
                {task.result ? shortValue(task.result) : "-"}
                {task.result && (
                  <CopyButton
                    value={
                      typeof task.result === "string"
                        ? task.result
                        : formatJson(task.result)
                    }
                    title="Скопировать результат"
                  />
                )}
              </span>
            </td>
          </tr>
        );
        const children =
          hasChildren && isExpanded ? (
            <React.Fragment key={`children-${task.id}`}>
              {TaskTableRows({
                tasks: task.children!,
                level: level + 1,
                expanded,
                toggleExpand,
              })}
            </React.Fragment>
          ) : null;
        return [row, children].filter(Boolean);
      })}
    </>
  );
}

export default function GenerateTasksPage() {
  const [tasks, setTasks] = useState<TaskOut[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const fetchTasks = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setError(null);
      try {
        const apiHost = import.meta.env.VITE_API_HOST;
        const res = await fetch(`${apiHost}/api/v1/tasks/`);
        if (!res.ok) throw new Error("Ошибка загрузки тасков");
        const data = await res.json();
        setTasks(data);
      } catch (e: any) {
        setError(e.message || "Неизвестная ошибка");
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
    const interval = setInterval(fetchTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  const tree = buildTaskTree(tasks);

  const toggleExpand = (task: TaskOut & { children?: TaskOut[] }) => {
    setExpanded((prev) => {
      const isNowExpanded = !prev[task.id];
      if (isNowExpanded) {
        return expandAllChildren(task, prev);
      } else {
        const collapse = (
          t: TaskOut & { children?: TaskOut[] },
          acc: Record<string, boolean>,
        ): Record<string, boolean> => {
          let res = { ...acc, [t.id]: false };
          if (t.children && t.children.length > 0) {
            for (const child of t.children) {
              res = collapse(child, res);
            }
          }
          return res;
        };
        return collapse(task, prev);
      }
    });
  };

  return (
    <div className="mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">
        Задачи генерации{" "}
        {loading && (
          <span className="loading loading-spinner loading-sm text-base-content"></span>
        )}
      </h1>
      {error && <div className="text-error">{error}</div>}
      <div className="overflow-x-auto max-h-[80vh] overflow-y-auto">
        <table className="table table-xs table-zebra w-full">
          <thead>
            <tr>
              <th>Тип</th>
              <th>ID</th>
              <th>Статус</th>
              <th>Создан</th>
              <th>Начат</th>
              <th>Завершён</th>
              <th>Длительность</th>
              <th>Ошибка</th>
              <th>Сессия</th>
              <th>Пользователь</th>
              <th>Параметры</th>
              <th>Результат</th>
            </tr>
          </thead>
          <tbody>
            {TaskTableRows({ tasks: tree, expanded, toggleExpand })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
