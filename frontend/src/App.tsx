import { useEffect, useState, useRef } from "react";
import type { FormEvent } from "react";
import type { UserManager, User } from "oidc-client-ts";
import createClient from "openapi-fetch";
import type { paths, components } from "./generated/api";
import { manager, type PublicConfig } from "./auth";
import { japanDate, japanInput, logoutLocation, message } from "./logic";
type Resource = components["schemas"]["ResourceItemResponse"];
type Reservation = components["schemas"]["ReservationItemResponse"];
type Detail = components["schemas"]["GetReservationResponse"];
type BusySlot = components["schemas"]["ScheduleSlotResponse"];
type ErrorBody = components["schemas"]["ErrorResponse"];
const PAGE = 20;
// 継続tokenは前へ戻れないため、表示中ページまでのtokenを積んで戻る。
const current = (pages: (string | undefined)[]) => pages[pages.length - 1];
const format = (s: string) =>
  new Intl.DateTimeFormat("ja-JP", {
    timeZone: "Asia/Tokyo",
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(s));

export default function App() {
  const [config, setConfig] = useState<PublicConfig>();
  const [auth, setAuth] = useState<UserManager>();
  const [user, setUser] = useState<User | null>(null);
  const [tab, setTab] = useState("resources");
  const [resources, setResources] = useState<Resource[]>([]);
  const [selected, setSelected] = useState<Resource>();
  const [day, setDay] = useState(japanDate(new Date(Date.now() + 86400000)));
  const [slots, setSlots] = useState<BusySlot[]>([]);
  const [mine, setMine] = useState<Reservation[]>([]);
  const [detail, setDetail] = useState<Detail>();
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [filter, setFilter] = useState("future");
  const [mineDay, setMineDay] = useState("");
  const [minePages, setMinePages] = useState<(string | undefined)[]>([
    undefined,
  ]);
  const [mineNext, setMineNext] = useState<string>();
  const [resourcePages, setResourcePages] = useState<(string | undefined)[]>([
    undefined,
  ]);
  const [resourceNext, setResourceNext] = useState<string>();
  const [edit, setEdit] = useState<Resource>();
  const [purpose, setPurpose] = useState("");
  const [start, setStart] = useState("10:00");
  const [end, setEnd] = useState("11:00");
  const request = useRef<{ body: string; key: string } | undefined>(undefined);
  const admin = Boolean(
    (user?.profile["cognito:groups"] as string[] | undefined)?.includes(
      "admin",
    ) ||
    (
      user?.profile.realm_access as { roles?: string[] } | undefined
    )?.roles?.includes("admin"),
  );
  const client = createClient<paths>({
    baseUrl: config?.api,
    headers: { Authorization: "Bearer " + (user?.access_token ?? "") },
  });

  useEffect(() => {
    void (async () => {
      try {
        const response = await fetch("/config.json", { cache: "no-store" });
        if (!response.ok) throw new Error("公開設定を取得できません。");
        const settings = (await response.json()) as PublicConfig;
        setConfig(settings);
        const instance = manager(settings);
        setAuth(instance);
        instance.events.addAccessTokenExpired(() => {
          setUser(null);
          setError(
            "ログインの有効期限が切れました。再度ログインしてください。",
          );
        });
        if (new URLSearchParams(location.search).has("code")) {
          setUser(await instance.signinRedirectCallback());
          history.replaceState({}, "", location.pathname);
        }
      } catch {
        setError("認証を開始できません。設定または接続を確認してください。");
      }
    })();
  }, []);
  useEffect(() => {
    if (user) void loadResources();
  }, [user, resourcePages]);
  useEffect(() => {
    if (selected && user) void loadSchedule();
  }, [selected, day, user]);
  useEffect(() => {
    if (user && tab === "mine") void loadMine();
  }, [user, tab, filter, mineDay, minePages]);
  useEffect(() => {
    const id = new URLSearchParams(location.search).get("reservation");
    if (user && id) void loadDetail(id);
  }, [user]);
  useEffect(() => {
    const listener = () => {
      const id = new URLSearchParams(location.search).get("reservation");
      if (id) void loadDetail(id);
      else setDetail(undefined);
    };
    window.addEventListener("popstate", listener);
    return () => window.removeEventListener("popstate", listener);
  });
  async function logout() {
    // メモリ上のtokenを先に破棄し、OIDC側のsessionも終了する。
    const hint = user?.id_token;
    if (!auth || !config) return;
    await auth.removeUser();
    if (config.logoutUrl)
      location.assign(logoutLocation(config, location.origin + "/"));
    else await auth.signoutRedirect({ id_token_hint: hint });
  }
  async function task(work: () => Promise<void>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await work();
    } catch (e) {
      setError(e instanceof Error ? e.message : message(0));
    } finally {
      setBusy(false);
    }
  }
  function check(status: number, error?: ErrorBody) {
    // 業務理由は共通error schemaのdetails[0].reasonで受け取る。
    throw new Error(
      message(status, error?.error.details?.[0]?.reason ?? undefined),
    );
  }
  async function loadResources() {
    await task(async () => {
      const { data, error, response } = await client.GET("/resources", {
        params: { query: { limit: PAGE, nextToken: current(resourcePages) } },
      });
      if (error) check(response.status, error);
      setResources(data?.items ?? []);
      setResourceNext(data?.nextToken ?? undefined);
    });
  }
  async function loadSchedule() {
    if (!selected) return;
    await task(async () => {
      const found: BusySlot[] = [];
      let nextToken: string | undefined;
      do {
        const { data, error, response } = await client.GET(
          "/resources/{resourceId}/schedule",
          {
            params: {
              path: { resourceId: selected.resourceId },
              query: { day, limit: 100, nextToken },
            },
          },
        );
        if (error) check(response.status, error);
        found.push(...(data?.items ?? []));
        nextToken = data?.nextToken ?? undefined;
      } while (nextToken);
      setSlots(found);
    });
  }
  async function loadMine() {
    await task(async () => {
      const { data, error, response } = await client.GET("/reservations", {
        params: {
          query: {
            future: filter === "future",
            status:
              filter === "confirmed" || filter === "cancelled"
                ? filter
                : undefined,
            day: mineDay || undefined,
            limit: PAGE,
            nextToken: current(minePages),
          },
        },
      });
      if (error) check(response.status, error);
      setMine(data?.items ?? []);
      setMineNext(data?.nextToken ?? undefined);
    });
  }
  async function loadDetail(id: string) {
    await task(async () => {
      const { data, error, response } = await client.GET(
        "/reservations/{reservationId}",
        { params: { path: { reservationId: id } } },
      );
      if (error) check(response.status, error);
      setDetail(data);
    });
  }
  function openDetail(id: string) {
    history.pushState({}, "", "?reservation=" + encodeURIComponent(id));
    void loadDetail(id);
  }
  async function book(event: FormEvent) {
    event.preventDefault();
    if (!selected) return;
    await task(async () => {
      const body = {
        resourceId: selected.resourceId,
        startAt: japanInput(day + "T" + start),
        endAt: japanInput(day + "T" + end),
        purpose: purpose.trim(),
      };
      const encoded = JSON.stringify(body);
      if (request.current?.body !== encoded)
        request.current = { body: encoded, key: crypto.randomUUID() };
      const { data, error, response } = await client.POST("/reservations", {
        body,
        params: { header: { "Idempotency-Key": request.current.key } },
      });
      if (error) check(response.status, error);
      request.current = undefined;
      setPurpose("");
      await loadSchedule();
      setNotice("予約が確定しました。");
      if (data) openDetail(data.reservationId);
    });
  }
  async function cancel(reservation: Detail["reservation"]) {
    await task(async () => {
      const { data, error, response } = await client.POST(
        "/reservations/{reservationId}/cancel",
        {
          params: { path: { reservationId: reservation.reservationId } },
          body: { version: reservation.version },
        },
      );
      if (error) check(response.status, error);
      if (data) {
        await loadDetail(data.reservationId);
        if (tab === "mine") await loadMine();
        if (selected) await loadSchedule();
        setNotice("予約を取り消しました。");
      }
    });
  }
  async function saveResource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    await task(async () => {
      const common = {
        name: String(data.get("name")),
        description: String(data.get("description")),
        kind: String(data.get("kind")) as "room" | "equipment",
      };
      const result = edit
        ? await client.PUT("/resources/{resourceId}", {
            params: { path: { resourceId: edit.resourceId } },
            body: {
              ...common,
              active: data.get("active") === "on",
              version: edit.version,
            },
          })
        : await client.POST("/resources", { body: common });
      if (result.error) check(result.response.status, result.error);
      setEdit(undefined);
      form.reset();
      await loadResources();
      setNotice("資源を保存しました。");
    });
  }

  return (
    <>
      <a href="#main" className="skip">
        本文へ移動
      </a>
      <header>
        <a className="brand" href="/">
          SlotKeeper<span>会議室・備品予約</span>
        </a>
        <div className="account">
          {user ? (
            <>
              <span>{admin ? "管理者" : "利用者"}</span>
              <button
                className="quiet"
                onClick={() => {
                  setUser(null);
                  setDetail(undefined);
                  setMine([]);
                  setSlots([]);
                  setPurpose("");
                  request.current = undefined;
                  void logout();
                }}
              >
                ログアウト
              </button>
            </>
          ) : (
            <button
              disabled={!auth}
              onClick={() => void auth?.signinRedirect()}
            >
              ログイン
            </button>
          )}
        </div>
      </header>
      <main id="main">
        <div className="intro">
          <p className="eyebrow">MAKE ROOM FOR YOUR NEXT IDEA</p>
          <h1>
            空き時間を、
            <br className="mobile" />
            みんなの時間へ。
          </h1>
          <p>
            場所も、道具も。必要なときに、気持ちよく。
            <br />
            すべての日時は日本時間で表示します。
          </p>
        </div>
        {error && (
          <div role="alert" className="alert">
            {error}
            <button
              onClick={() =>
                selected ? void loadSchedule() : void loadResources()
              }
            >
              最新情報を確認
            </button>
          </div>
        )}
        {notice && (
          <div role="status" className="success">
            {notice}
          </div>
        )}
        {busy && <p role="status">読み込み・処理中…</p>}
        {!user ? (
          <section className="welcome">
            <h2>次の予定を、ここから。</h2>
            <p>ログインすると、空き時間の確認と予約ができます。</p>
            <button
              disabled={!auth}
              onClick={() => void auth?.signinRedirect()}
            >
              ログインして予約する →
            </button>
            <p className="muted">
              予約は15分から4時間まで。30日先まで受け付けます。
            </p>
          </section>
        ) : (
          <>
            <nav aria-label="メインメニュー">
              {[
                ["resources", "資源を探す"],
                ["mine", "自分の予約"],
                ...(admin ? [["admin", "資源管理"]] : []),
              ].map(([id, label]) => (
                <button
                  key={id}
                  aria-current={tab === id ? "page" : undefined}
                  onClick={() => {
                    setTab(id ?? "resources");
                    setSelected(undefined);
                  }}
                >
                  {label}
                </button>
              ))}
            </nav>
            {tab === "resources" && (
              <section>
                <div className="section-heading">
                  <h2>使いたい資源を選ぶ</h2>
                  <span>{resources.length}件を表示</span>
                </div>
                <div className="cards">
                  {resources.map((r) => (
                    <button
                      key={r.resourceId}
                      className={
                        "resource " +
                        (selected?.resourceId === r.resourceId
                          ? "selected"
                          : "")
                      }
                      onClick={() => setSelected(r)}
                    >
                      <span className="kind">
                        {r.kind === "room"
                          ? "ROOM / 会議室"
                          : "EQUIPMENT / 備品"}
                      </span>
                      <strong>{r.name}</strong>
                      <span>{r.description || "説明はありません"}</span>
                      <span className={r.active ? "available" : "muted"}>
                        {r.active ? "予約受付中" : "利用停止中"}
                      </span>
                    </button>
                  ))}
                </div>
                {!resources.length && !busy && (
                  <p>登録された資源はありません。</p>
                )}
                <div className="pagination">
                  <button
                    disabled={resourcePages.length === 1}
                    onClick={() => setResourcePages(resourcePages.slice(0, -1))}
                  >
                    前の資源
                  </button>
                  <button
                    disabled={!resourceNext}
                    onClick={() =>
                      setResourcePages([...resourcePages, resourceNext])
                    }
                  >
                    次の資源
                  </button>
                </div>
                {selected && (
                  <div className="booking-grid">
                    <section className="panel">
                      <h2>{selected.name} の予約表</h2>
                      <label>
                        日付
                        <input
                          type="date"
                          value={day}
                          onChange={(e) => setDay(e.target.value)}
                        />
                      </label>
                      <button
                        className="quiet"
                        onClick={() => void loadSchedule()}
                      >
                        最新の空き状況を取得
                      </button>
                      {slots.length === 0 && !busy ? (
                        <p className="empty">この日の予約はまだありません。</p>
                      ) : (
                        <ul className="slot-list">
                          {slots.map((slot, i) => (
                            <li key={i}>
                              <strong>
                                {format(slot.startAt)} — {format(slot.endAt)}
                              </strong>
                              <span>{slot.label}</span>
                              {slot.reservation && (
                                <button
                                  className="quiet"
                                  onClick={() =>
                                    openDetail(slot.reservation!.reservationId)
                                  }
                                >
                                  詳細・取消
                                </button>
                              )}
                            </li>
                          ))}
                        </ul>
                      )}
                    </section>
                    <form className="panel" onSubmit={(e) => void book(e)}>
                      <h2>この資源を予約</h2>
                      <p>
                        {day} · {selected.name}
                      </p>
                      <div className="time-grid">
                        <label>
                          開始
                          <input
                            required
                            type="time"
                            step="900"
                            value={start}
                            onChange={(e) => setStart(e.target.value)}
                          />
                        </label>
                        <label>
                          終了
                          <input
                            required
                            type="time"
                            step="900"
                            value={end}
                            onChange={(e) => setEnd(e.target.value)}
                          />
                        </label>
                      </div>
                      <label>
                        利用目的
                        <textarea
                          required
                          maxLength={200}
                          value={purpose}
                          onChange={(e) => setPurpose(e.target.value)}
                          placeholder="例：プロジェクトの打ち合わせ"
                        />
                      </label>
                      <p className="muted">
                        同じ日の15分〜4時間。目的は本人と管理者だけが閲覧できます。
                      </p>
                      <button disabled={busy || !selected.active}>
                        予約を確定する
                      </button>
                    </form>
                  </div>
                )}
              </section>
            )}
            {tab === "mine" && (
              <section>
                <h2>自分の予約</h2>
                <div className="filters">
                  <label>
                    状態
                    <select
                      value={filter}
                      onChange={(e) => {
                        setFilter(e.target.value);
                        setMinePages([undefined]);
                      }}
                    >
                      <option value="future">開始前の予約</option>
                      <option value="all">すべて</option>
                      <option value="confirmed">確定</option>
                      <option value="cancelled">取消済み</option>
                    </select>
                  </label>
                  <label>
                    日付
                    <input
                      type="date"
                      value={mineDay}
                      onChange={(e) => {
                        setMineDay(e.target.value);
                        setMinePages([undefined]);
                      }}
                    />
                  </label>
                </div>
                {!mine.length && !busy && (
                  <p className="empty">条件に合う予約はありません。</p>
                )}
                <ul className="reservation-list">
                  {mine.map((r) => (
                    <li key={r.reservationId}>
                      <div>
                        <strong>{r.purpose}</strong>
                        <p>
                          {format(r.startAt)} — {format(r.endAt)}
                        </p>
                        <span>
                          {r.status === "cancelled"
                            ? "取消済み"
                            : new Date(r.endAt) < new Date()
                              ? "終了"
                              : "確定"}
                        </span>
                      </div>
                      <button onClick={() => openDetail(r.reservationId)}>
                        詳細・履歴
                      </button>
                    </li>
                  ))}
                </ul>
                <div className="pagination">
                  <button
                    disabled={minePages.length === 1}
                    onClick={() => setMinePages(minePages.slice(0, -1))}
                  >
                    前の予約
                  </button>
                  <button
                    disabled={!mineNext}
                    onClick={() => setMinePages([...minePages, mineNext])}
                  >
                    次の予約
                  </button>
                </div>
              </section>
            )}
            {tab === "admin" && admin && (
              <section>
                <h2>資源管理</h2>
                <div className="booking-grid">
                  <div>
                    {resources.map((r) => (
                      <div className="admin-row" key={r.resourceId}>
                        <span>
                          {r.name} · {r.active ? "有効" : "無効"}
                        </span>
                        <button onClick={() => setEdit(r)}>編集</button>
                      </div>
                    ))}
                  </div>
                  <form
                    key={edit?.resourceId ?? "new"}
                    className="panel"
                    onSubmit={(e) => void saveResource(e)}
                  >
                    <h3>{edit ? "資源を編集：" + edit.name : "資源を追加"}</h3>
                    <label>
                      資源名
                      <input
                        name="name"
                        required
                        maxLength={100}
                        defaultValue={edit?.name}
                      />
                    </label>
                    <label>
                      種類
                      <select name="kind" defaultValue={edit?.kind ?? "room"}>
                        <option value="room">会議室</option>
                        <option value="equipment">備品</option>
                      </select>
                    </label>
                    <label>
                      説明
                      <textarea
                        name="description"
                        maxLength={1000}
                        defaultValue={edit?.description}
                      />
                    </label>
                    {edit && (
                      <label className="checkbox">
                        <input
                          type="checkbox"
                          name="active"
                          defaultChecked={edit.active}
                        />
                        予約を受け付ける
                      </label>
                    )}
                    <button disabled={busy}>資源を保存</button>
                    {edit && (
                      <button
                        type="button"
                        className="quiet"
                        onClick={() => setEdit(undefined)}
                      >
                        追加に戻る
                      </button>
                    )}
                  </form>
                </div>
              </section>
            )}
            {detail && (
              <section className="panel detail" aria-label="予約詳細">
                <div className="section-heading">
                  <h2>予約詳細・履歴</h2>
                  <button
                    className="quiet"
                    onClick={() => {
                      setDetail(undefined);
                      history.pushState({}, "", "/");
                    }}
                  >
                    閉じる
                  </button>
                </div>
                <h3>{detail.reservation.purpose}</h3>
                <p>
                  資源：
                  {resources.find(
                    (r) => r.resourceId === detail.reservation.resourceId,
                  )?.name ?? detail.reservation.resourceId}
                </p>
                <p>
                  {format(detail.reservation.startAt)} —{" "}
                  {format(detail.reservation.endAt)}
                </p>
                <p>
                  状態：
                  {detail.reservation.status === "confirmed"
                    ? "確定"
                    : "取消済み"}{" "}
                  · 版 {detail.reservation.version}
                </p>
                <ol>
                  {detail.events.map((e) => (
                    <li key={e.eventId}>
                      {format(e.occurredAt)} ·{" "}
                      {e.action === "created" ? "予約を作成" : "予約を取消"}
                    </li>
                  ))}
                </ol>
                {detail.reservation.status === "confirmed" &&
                  new Date(detail.reservation.startAt) > new Date() && (
                    <button
                      className="danger"
                      disabled={busy}
                      onClick={() => void cancel(detail.reservation)}
                    >
                      この予約を取り消す
                    </button>
                  )}
              </section>
            )}
          </>
        )}
      </main>
      <footer>
        SlotKeeper <span>余白をつくる、予約のかたち。</span>
      </footer>
    </>
  );
}
