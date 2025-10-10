// 1. Interface defining the props for UserMessageComponent, expecting a 'message' of type string.
interface UserMessageComponentProps {
    message: string;
}

// 2. UserMessageComponent functional component that renders a message within styled div elements.
const UserMessageComponent: React.FC<UserMessageComponentProps> = ({ message }) => {
    return (
        <div className="dark:bg-slate-800 bg-white shadow-lg rounded-lg p-4 mt-4">
            <div className="flex items-center">
                {/* 3. Render Message component*/}
                <h2 className="text-lg font-semibold flex-grow dark:text-white text-black">{message}</h2>
            </div>
        </div>
    );
};

export default UserMessageComponent;