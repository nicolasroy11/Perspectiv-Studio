import { FaInstagram, FaTiktok, FaSoundcloud, FaYoutube } from "react-icons/fa";

export function MusicPage() {
  return (
    <div
      style={{
        minHeight: "100vh",
        width: "100%",
        backgroundColor: "#0a0f1a",
        color: "#ddd",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "80px 20px",
        textAlign: "center",
      }}
    >
      <h1
        style={{
          fontSize: "42px",
          color: "white",
          marginBottom: "40px",
        }}
      >
        Perspectiv Music
      </h1>

      <p
        style={{
          maxWidth: "650px",
          fontSize: "18px",
          lineHeight: 1.6,
          marginBottom: "70px",
          color: "#c9c9c9",
        }}
      >
        A new sonic vision is emerging — cinematic beats, emotional chord progressions,
        and genre-bending production.
        <br />
        Full releases coming soon.
      </p>

      {/* SOCIAL BUTTONS */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "30px",
        }}
      >
        {/* Instagram */}
        <a
          href="https://www.instagram.com/perspectiv.music/"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            fontSize: "22px",
            padding: "20px 40px",
            borderRadius: "50px",
            backgroundColor: "#E1306C",
            color: "white",
            textDecoration: "none",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          <FaInstagram size={28} />
          Instagram
        </a>

        {/* TikTok */}
        <a
          href="https://www.tiktok.com/@perspectiv.music"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            fontSize: "22px",
            padding: "20px 40px",
            borderRadius: "50px",
            backgroundColor: "#000",
            border: "2px solid rgba(255,255,255,0.2)",
            color: "white",
            textDecoration: "none",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          <FaTiktok size={28} />
          TikTok
        </a>

        <a
          href="https://soundcloud.com/perspectiv-music"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            fontSize: "22px",
            padding: "20px 40px",
            borderRadius: "50px",
            backgroundColor: "#ff5500",
            color: "white",
            textDecoration: "none",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          <FaSoundcloud size={28} />
          SoundCloud
        </a>

        <a
          href="https://www.youtube.com/@perspectiv_music"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            fontSize: "22px",
            padding: "20px 40px",
            borderRadius: "50px",
            backgroundColor: "#FF0000",
            color: "white",
            textDecoration: "none",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
  <FaYoutube size={28} />
  YouTube
</a>
      </div>

      <p
        style={{
          marginTop: "60px",
          fontSize: "14px",
          color: "#888",
        }}
      >
        Page in development — new releases dropping soon.
      </p>
    </div>
  );
}
