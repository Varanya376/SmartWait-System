function JoinQueue({ restaurant }) {

    const handleJoin = () => {
      alert(`Joined queue at ${restaurant.name}`);
    };
  
    return (
      <button className="join-btn" onClick={handleJoin}>
        Join Queue
      </button>
    );
  }
  
  export default JoinQueue;