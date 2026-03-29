import Spline from '@splinetool/react-spline';

export function KredBird({ className = '' }) {
  function onLoad(spline) {
    spline.setZoom(0.18);
  }

  return (
    <div className={`fixed bottom-6 right-6 w-24 h-24 md:w-32 md:h-32 z-40 ${className}`}>
      <div style={{ width: '100%', height: '160%', overflow: 'hidden' }}>
        <Spline 
          scene="https://prod.spline.design/bUDuHGHrqOSQKxWh/scene.splinecode" 
          onLoad={onLoad}
        />
      </div>
    </div>
  );
}
