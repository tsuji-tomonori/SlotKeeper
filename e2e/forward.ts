import net from "node:net";
// verifyコンテナ内のChromiumから、利用者のブラウザと同じlocalhostのURLで
// web・API・OIDCへ到達させる。page.routeでの書換えはOIDCの302後の遷移を
// 取りこぼすため、TCPで転送してissuer・callback URLを本番同様に扱う。
const targets: [number, string | undefined][] = [
  [4321, process.env.SLOT_WEB_URL],
  [8000, process.env.SLOT_API_URL],
  [8080, process.env.SLOT_OIDC_INTERNAL],
];
function listen(server: net.Server, port: number, host: string) {
  return new Promise<void>((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, host, () => {
      server.off("error", reject);
      resolve();
    });
  });
}
export default async function setup() {
  const servers: net.Server[] = [];
  for (const [port, target] of targets) {
    if (!target) continue;
    const url = new URL(target);
    for (const host of ["127.0.0.1", "::1"]) {
      const server = net.createServer((client) => {
        const upstream = net.connect(Number(url.port), url.hostname);
        client.pipe(upstream).pipe(client);
        client.on("error", () => upstream.destroy());
        upstream.on("error", () => client.destroy());
      });
      try {
        await listen(server, port, host);
        servers.push(server);
      } catch (error) {
        // IPv6が無効なコンテナでは::1を使わない。IPv4の失敗は隠さない。
        if (host === "127.0.0.1") throw error;
      }
    }
  }
  return async () => {
    await Promise.all(
      servers.map((s) => new Promise((resolve) => s.close(resolve))),
    );
  };
}
