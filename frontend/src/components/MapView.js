import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";
import L from "leaflet";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
    iconUrl: markerIcon,
    iconRetinaUrl: markerIcon2x,   
    shadowUrl: markerShadow,

    iconSize: [25, 41],           
    iconAnchor: [12, 41],         
    popupAnchor: [1, -34],        
    shadowSize: [41, 41],
});

const getColor = (wait) => {
    if (!wait) return "blue";
    if (wait <= 5) return "green";
    if (wait <= 20) return "orange";
    return "red";
};

// ✅ Resize fix
function ResizeMap() {
    const map = useMap();

    useEffect(() => {
        const timer = setTimeout(() => {
            map.invalidateSize();
        }, 500);

        return () => clearTimeout(timer);
    }, [map]);

    return null;
}

function MapView({ restaurants, userLocation }) {

    // ✅ NEW: dynamic center
    const center = userLocation
        ? [userLocation.lat, userLocation.lng]
        : [51.509, -0.12];

    // ✅ FIX: move condition OUTSIDE JSX
    if (!restaurants || restaurants.length === 0) {
        return <p style={{ textAlign: "center" }}>Loading map...</p>;
    }

    return (
        <MapContainer
            center={center}
            zoom={13}
            style={{ height: "300px", width: "100%" }}
            preferCanvas={true}
        >
            <ResizeMap />

            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                errorTileUrl="https://via.placeholder.com/256?text=."
                maxZoom={19}
            />

            {restaurants
                .filter(r => r.lat && r.lng)
                .map((r) => (
                    <Marker key={r.id} position={[r.lat, r.lng]}>
                        <Popup>
                            <b>{r.name}</b><br />
                            📍 {r.distance?.toFixed(1)} km<br />
                            <span style={{ color: getColor(r.wait_time) }}>
                                ⏱ {r.wait_time ?? "Live..."} mins
                            </span>
                        </Popup>
                    </Marker>
                ))}
        </MapContainer>
    );
}

export default MapView;